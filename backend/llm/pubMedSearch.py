import os
import json
import requests
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
from .extract_relevant_text import get_relevant_chunks
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))


# Configuration
ENTREZ_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EMAIL = os.getenv("EMAIL")
NCBI_API_KEY = os.getenv("NCBI_API_KEY")  # προαιρετικό, ανεβάζει rate limit σε 10 req/sec
FETCH_LIMIT = 8    # μειώθηκε από 15 — λιγότερα άρθρα, πολύ πιο γρήγορο
MAX_KEYWORDS = 5   # χρησιμοποιούμε τα 5 πιο σχετικά keywords αντί για όλα


def make_session() -> requests.Session:
    session = requests.Session()
    # Μόνο 1 retry με μικρό backoff — δεν θέλουμε να χάνουμε χρόνο σε αποτυχημένα requests
    retries = Retry(total=1, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session


def build_query(keywords: list[str]) -> str:
    # Παίρνουμε μόνο τα πρώτα MAX_KEYWORDS για πιο στοχευμένη αναζήτηση
    top_keywords = keywords[:MAX_KEYWORDS]
    return " OR ".join(f'"{kw}"[MeSH Terms]' for kw in top_keywords)


def search_pubmed(query: str, max_results: int = FETCH_LIMIT) -> list[str]:
    """Searches PubMed and returns PMIDs sorted by relevance."""
    url = f"{ENTREZ_BASE}/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "sort": "relevance",
        "retmode": "json",
        "email": EMAIL,
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY

    session = make_session()
    response = session.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()
    pmids = data.get("esearchresult", {}).get("idlist", [])
    return pmids


def fetch_metadata(pmids: list[str]) -> list[dict]:
    """
    Downloads metadata (title, authors, journal, year, doi, pmcid)
    for the given PMIDs in a single batch request.
    """
    if not pmids:
        return []

    url = f"{ENTREZ_BASE}/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "email": EMAIL,
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY

    session = make_session()
    response = session.get(url, params=params, timeout=30)
    response.raise_for_status()

    return parse_metadata_xml(response.text)


def parse_metadata_xml(xml_text: str) -> list[dict]:
    """Parses the XML from NCBI and extracts article metadata."""
    root = ET.fromstring(xml_text)
    articles = []

    for article_node in root.findall(".//PubmedArticle"):
        pmid_node = article_node.find(".//PMID")
        pmid = pmid_node.text if pmid_node is not None else "N/A"

        title_node = article_node.find(".//ArticleTitle")
        title = "".join(title_node.itertext()) if title_node is not None else "No title"

        author_nodes = article_node.findall(".//Author")
        authors = []
        for a in author_nodes:
            last = a.findtext("LastName", "")
            fore = a.findtext("ForeName", "")
            if last:
                initials = " ".join(f"{n[0]}." for n in fore.split()) if fore else ""
                authors.append(f"{last}, {initials}".strip(", "))

        journal = article_node.findtext(".//Journal/Title",       "Unknown journal")
        year    = article_node.findtext(".//PubDate/Year",        "n.d.")
        volume  = article_node.findtext(".//JournalIssue/Volume", "")
        issue   = article_node.findtext(".//JournalIssue/Issue",  "")
        pages   = article_node.findtext(".//MedlinePgn",          "")
        doi     = article_node.findtext(".//ArticleId[@IdType='doi']", None)
        pmcid   = article_node.findtext(".//ArticleId[@IdType='pmc']", None)

        articles.append({
            "pmid":    pmid,
            "pmcid":   pmcid,
            "title":   title,
            "authors": authors,
            "journal": journal,
            "year":    year,
            "volume":  volume,
            "issue":   issue,
            "pages":   pages,
            "doi":     doi,
            "url":     f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        })

    return articles


def build_apa_citation(article: dict) -> str:
    """Builds APA 7th edition citation."""
    authors = article["authors"]

    if not authors:
        author_str = "Unknown Author"
    elif len(authors) == 1:
        author_str = authors[0]
    elif len(authors) <= 20:
        author_str = ", ".join(authors[:-1]) + f", & {authors[-1]}"
    else:
        author_str = ", ".join(authors[:19]) + f", ... {authors[-1]}"

    vol_issue = article["volume"]
    if article["issue"]:
        vol_issue += f"({article['issue']})"

    parts = [
        f"{author_str} ({article['year']}).",
        f"{article['title']}.",
        f"{article['journal']}",
        f", {vol_issue}" if vol_issue else "",
        f", {article['pages']}" if article["pages"] else "",
        ".",
        f" https://doi.org/{article['doi']}" if article["doi"] else f" {article['url']}",
    ]
    return "".join(parts)


def fetch_full_text(pmcid: str) -> str | None:
    params = {
        "db":      "pmc",
        "id":      pmcid,
        "retmode": "xml",
        "rettype": "full",
        "email":   EMAIL,
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY
    try:
        session = make_session()
        # Timeout μειώθηκε από 60s σε 15s — αν αργεί τόσο, το παρακάμπτουμε
        r = session.get(f"{ENTREZ_BASE}/efetch.fcgi", params=params, timeout=15)
        r.raise_for_status()
        return _extract_text_from_pmc_xml(r.text)
    except Exception as e:
        print(f"  Failed to fetch full text for {pmcid}: {e}")
        return None


def _extract_text_from_pmc_xml(xml_text: str) -> str:
    root = ET.fromstring(xml_text)
    chunks = []

    for elem in root.iter():
        if elem.tag == "title":
            text = "".join(elem.itertext()).strip()
            if text:
                chunks.append(f"\n## {text}\n")
        elif elem.tag == "p":
            text = "".join(elem.itertext()).strip()
            if text:
                chunks.append(text)

    return "\n".join(chunks).strip()


def get_top_papers(ai_diagnosis):
    """
    1. Builds PubMed query from the top MAX_KEYWORDS keywords
    2. Fetches the most relevant PMIDs (FETCH_LIMIT)
    3. Filters for open-access articles only
    4. Fetches full texts in parallel (max_workers=10)
    5. Returns ranked relevant chunks
    """
    keywords = ai_diagnosis["pubmed_keywords"]
    print(f"Keywords (using top {MAX_KEYWORDS}): {keywords[:MAX_KEYWORDS]}")
    query = build_query(keywords)
    print(f"Query: {query}\n")

    pmids = list(dict.fromkeys(search_pubmed(query, max_results=FETCH_LIMIT)))
    if not pmids:
        print("No results found.")
        return []

    print(f"{len(pmids)} articles found. Checking open access...\n")

    articles = fetch_metadata(pmids)

    def fetch_article(article):
        pmcid = article["pmcid"]
        if not pmcid:
            print(f" [{article['pmid']}] {article['title'][:60]}… — closed access, skip")
            return None

        print(f" [{article['pmid']}] {article['title'][:60]}… — fetching...")
        full_text = fetch_full_text(pmcid)
        if not full_text:
            return None
        return {
            "url":      article["url"],
            "title":    article["title"],
            "citation": build_apa_citation(article),
            "text":     full_text,
        }

    papers = []
    # max_workers ανέβηκε από 5 σε 10 — διπλάσια παραλληλία για τα HTTP requests
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_article, a): a for a in articles}
        for future in as_completed(futures):
            result = future.result()
            if result:
                papers.append(result)

    if not papers:
        print("No open access articles found.")
        return []

    return get_relevant_chunks(ai_diagnosis["combined_diagnosis"], papers)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from .prompts import PUBMEDSEARCH_TEST

    ai_diagnosis = PUBMEDSEARCH_TEST
    papers = get_top_papers(ai_diagnosis)
    print(json.dumps(papers, ensure_ascii=False, indent=2))