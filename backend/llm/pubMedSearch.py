import json
import requests
import xml.etree.ElementTree as ET
import time
from extract_relevant_text import get_relevant_chunks
from concurrent.futures import ThreadPoolExecutor, as_completed

#configuration
ENTREZ_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EMAIL = "ics24128@uom.edu.gr"
FETCH_LIMIT = 20


def build_query(keywords: list[str]) -> str:
    #keywords are combined in a pubMed query string
    return " OR ".join(f'"{kw}"[MeSH Terms]' for kw in keywords)

def search_pubmed(query: str, max_results: int = FETCH_LIMIT) -> list[str]:
    
    #Searches in pubMed and returns the PMIDs (sorted by relevance by NCBI)
    
    url = f"{ENTREZ_BASE}/esearch.fcgi" #calls the 'esearch' NBCI's endpoint
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "sort": "relevance",   # NCBI returns the most relevant ones first
        "retmode": "json",
        "email": EMAIL,
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()
    pmids = data.get("esearchresult", {}).get("idlist", [])
    return pmids


def fetch_metadata(pmids: list[str]) -> list[dict]:
    """
    Downloads the metadata (title, authors, journal, year, doi, pmcid)
    for the given PMIDs.
    """
    if not pmids:
        return []

    url = f"{ENTREZ_BASE}/efetch.fcgi" #calls the 'efetch' NBCI's endpoint to get the full xml with the article's info
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "email": EMAIL,
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    return parse_metadata_xml(response.text)


def parse_metadata_xml(xml_text: str) -> list[dict]:
    #analyzes the xml returned from NCBI and extracts each article's metadata
    root = ET.fromstring(xml_text)
    articles = []

    for article_node in root.findall(".//PubmedArticle"):
        # PMID
        pmid_node = article_node.find(".//PMID")
        pmid = pmid_node.text if pmid_node is not None else "N/A"

        # title
        title_node = article_node.find(".//ArticleTitle")
        title = "".join(title_node.itertext()) if title_node is not None else "No title"

        # Authors
        author_nodes = article_node.findall(".//Author")
        authors = []
        for a in author_nodes:          
            last = a.findtext("LastName", "")
            fore = a.findtext("ForeName", "")
            if last:
                # APA format: Last, F.
                initials = " ".join(f"{n[0]}." for n in fore.split()) if fore else ""
                authors.append(f"{last}, {initials}".strip(", "))

        # Journal, year, volume, issue, pages
        journal = article_node.findtext(".//Journal/Title",         "Unknown journal")
        year    = article_node.findtext(".//PubDate/Year",          "n.d.")
        volume  = article_node.findtext(".//JournalIssue/Volume",   "")
        issue   = article_node.findtext(".//JournalIssue/Issue",    "")
        pages   = article_node.findtext(".//MedlinePgn",            "")

        # DOI
        doi = article_node.findtext(".//ArticleId[@IdType='doi']", None)

        # PMCID (which exists only if the article provides open access)
        pmcid = article_node.findtext(".//ArticleId[@IdType='pmc']", None)

        articles.append({
            "pmid":        pmid,
            "pmcid":       pmcid,
            "title":       title,
            "authors":     authors,
            "journal":     journal,
            "year":        year,
            "volume":      volume,
            "issue":       issue,
            "pages":       pages,
            "doi":         doi,
            "url":         f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        })

    return articles


def build_apa_citation(article: dict) -> str:
    """
    Builds APA 7th edition citation.
    Form: Last, F., & Last, F. (year). Title. Journal, volume(issue), pages. DOI
    """
    authors = article["authors"]

    if not authors:
        author_str = "Unknown Author"
    elif len(authors) == 1:
        author_str = authors[0]
    elif len(authors) <= 20:
        author_str = ", ".join(authors[:-1]) + f", & {authors[-1]}"
    else:
        # APA: πρώτοι 19, ... , τελευταίος
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
    try:
        r = requests.get(f"{ENTREZ_BASE}/efetch.fcgi", params=params, timeout=30)
        r.raise_for_status()
        return _extract_text_from_pmc_xml(r.text)
    except Exception as e:
        print(f"  Failed to fetch full text for the article: {pmcid}: {e}")
        return None
    
def _extract_text_from_pmc_xml(xml_text: str) -> str:
    root   = ET.fromstring(xml_text)
    chunks = []

    for elem in root.iter():
        # titles of units
        if elem.tag == "title":
            text = "".join(elem.itertext()).strip()
            if text:
                chunks.append(f"\n## {text}\n")
        # Paragraphs
        elif elem.tag == "p":
            text = "".join(elem.itertext()).strip()
            if text:
                chunks.append(text)

    return "\n".join(chunks).strip()

def get_top_papers(ai_diagnosis) -> list[dict]:
    """
    1. Builds the query from given keywords for PubMed
    2. Fetches the most relevant PMIDs
    3. Checks which articles provide open access
    4. Fetches full text for each one of them
    5. Returns a json list which contains the following information: url, title, citation (APA), full_text
    """
    keywords = ai_diagnosis["pubmed_keywords"]
    print(f"Keywords : {keywords}")
    query = build_query(keywords)
    print(f"Query    : {query}\n")

    pmids = search_pubmed(query, max_results=FETCH_LIMIT)
    if not pmids:
        print("No results found")
        return []

    print(f"{len(pmids)} articles were found. Checking open access...\n")

    articles = fetch_metadata(pmids)

    def fetch_article(article):
        pmcid = article["pmcid"]
        if not pmcid:
            print(f" [{article['pmid']}] {article['title'][:60]}… — closed access, dismiss")
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
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_article, a): a for a in articles}
        for future in as_completed(futures):
            result = future.result()
            if result:
                papers.append(result)

    return get_relevant_chunks(ai_diagnosis["combined_diagnosis"], papers)

# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
   
    ai_diagnosis = {
        "consistent": True,
        "combined_diagnosis": "The patient presents with headache, productive cough, and low-grade fever (approximately 37.1–37.9°C), a symptom cluster most consistent with an acute respiratory tract infection, most likely of viral etiology. The differential diagnosis includes acute viral bronchitis and viral upper respiratory infection (common cold) as the leading possibilities. Other potential causes include influenza, COVID-19 infection, early or mild community-acquired pneumonia if symptoms worsen or sputum becomes purulent, and acute sinusitis with post-nasal drip contributing to cough and headache. Recommended evaluation includes monitoring vital signs (temperature, respiratory rate, and oxygen saturation), performing lung auscultation, and assessing sputum characteristics. Diagnostic testing such as COVID-19 or influenza testing may be appropriate, with additional laboratory studies (e.g., CBC, CRP) and chest radiography considered if bacterial infection or pneumonia is suspected. Medical evaluation is recommended if symptoms persist for several days, worsen, or are accompanied by high fever, shortness of breath, chest pain, or significant fatigue.",
        "pubmed_keywords": [
            "Acute Bronchitis",
            "Upper Respiratory Tract Infections",
            "Influenza, Human",
            "COVID-19",
            "Community-Acquired Pneumonia",
            "Cough",
            "Fever",
            "Respiratory Tract Infections",
            "Sputum",
            "Chest Radiography"
        ]
    }
    
    papers = get_top_papers(ai_diagnosis)
# Printing as JSON
    print(json.dumps(papers, ensure_ascii=False, indent=2))