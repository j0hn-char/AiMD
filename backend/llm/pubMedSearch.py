import os
import json
import asyncio
import httpx
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from .extract_relevant_text import get_relevant_chunks

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

ENTREZ_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EMAIL = os.getenv("EMAIL")
NCBI_API_KEY = os.getenv("NCBI_API_KEY")
FETCH_LIMIT = 15


# ── Helpers ────────────────────────────────────────────────────────────────────

def _base_params(extra: dict) -> dict:
    p = {"email": EMAIL, **extra}
    if NCBI_API_KEY:
        p["api_key"] = NCBI_API_KEY
    return p

def _make_client() -> httpx.AsyncClient:
    transport = httpx.AsyncHTTPTransport(retries=3)
    return httpx.AsyncClient(transport=transport, timeout=60)

def build_query(keywords: list[str]) -> str:
    return " OR ".join(f'"{kw}"[MeSH Terms]' for kw in keywords)


# ── Pure XML parsers (no I/O — no changes needed) ─────────────────────────────

def parse_metadata_xml(xml_text: str) -> list[dict]:
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


def build_apa_citation(article: dict) -> str:
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


# ── Async network calls ────────────────────────────────────────────────────────

async def search_pubmed(client: httpx.AsyncClient, query: str, max_results: int = FETCH_LIMIT) -> list[str]:
    params = _base_params({
        "db": "pubmed", "term": query,
        "retmax": max_results, "sort": "relevance", "retmode": "json",
    })
    r = await client.get(f"{ENTREZ_BASE}/esearch.fcgi", params=params)
    r.raise_for_status()
    return r.json().get("esearchresult", {}).get("idlist", [])


async def fetch_metadata(client: httpx.AsyncClient, pmids: list[str]) -> list[dict]:
    if not pmids:
        return []
    params = _base_params({"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"})
    r = await client.get(f"{ENTREZ_BASE}/efetch.fcgi", params=params)
    r.raise_for_status()
    return parse_metadata_xml(r.text)


async def fetch_full_text(client: httpx.AsyncClient, pmcid: str) -> str | None:
    params = _base_params({"db": "pmc", "id": pmcid, "retmode": "xml", "rettype": "full"})
    try:
        r = await client.get(f"{ENTREZ_BASE}/efetch.fcgi", params=params)
        r.raise_for_status()
        return _extract_text_from_pmc_xml(r.text)
    except Exception as e:
        print(f"  Failed to fetch full text for {pmcid}: {e}")
        return None


async def _fetch_article(client: httpx.AsyncClient, article: dict) -> dict | None:
    pmcid = article["pmcid"]
    if not pmcid:
        print(f" [{article['pmid']}] {article['title'][:60]}… — closed access, skipping")
        return None
    print(f" [{article['pmid']}] {article['title'][:60]}… — fetching...")
    full_text = await fetch_full_text(client, pmcid)
    if not full_text:
        return None
    return {
        "url":      article["url"],
        "title":    article["title"],
        "citation": build_apa_citation(article),
        "text":     full_text,
    }


# ── Main entry point ───────────────────────────────────────────────────────────

async def get_top_papers(ai_diagnosis: dict) -> list:
    keywords = ai_diagnosis["pubmed_keywords"]
    query = build_query(keywords)
    print(f"Keywords : {keywords}\nQuery    : {query}\n")

    async with _make_client() as client:
        pmids = list(dict.fromkeys(await search_pubmed(client, query)))
        if not pmids:
            print("No results found")
            return []

        print(f"{len(pmids)} articles found. Fetching metadata + full texts concurrently...\n")

        articles = await fetch_metadata(client, pmids)

        # All open-access full-text fetches fire at the same time
        results = await asyncio.gather(*[_fetch_article(client, a) for a in articles])

    papers = [r for r in results if r is not None]

    if not papers:
        print("No open access articles found.")
        return []

    return get_relevant_chunks(ai_diagnosis["combined_diagnosis"], papers)


if __name__ == "__main__":
    from .prompts import PUBMEDSEARCH_TEST
    papers = asyncio.run(get_top_papers(PUBMEDSEARCH_TEST))
    print(json.dumps(papers, ensure_ascii=False, indent=2))