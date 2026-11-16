"""Public bibliographic ingestion. No AI, no summary generation, no fulltext scraping."""
from __future__ import annotations

import os
import re
import time
import logging
from datetime import date, timedelta
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup

from .config import (TOPICS, JOURNALS, CATEGORIES, OFFICIAL_PAGES, OFFICIAL_HOSTS,
                     GUIDE_WORDS, COMMUNICATION_WORDS, NEWS_WORDS)

LOG = logging.getLogger(__name__)
EUTIL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "ElAlmaque/0.1 (academic bibliography; see project README)"})


def get(url, params=None):
    for retry in range(3):
        try:
            result = SESSION.get(url, params=params, timeout=25)
            result.raise_for_status()
            return result
        except requests.RequestException:
            if retry == 2:
                raise
            time.sleep(2 ** retry)


def tag_text(node):
    return " ".join("".join(node.itertext()).split()) if node is not None else ""


def topic_for(text):
    hay = text.lower()
    return [topic for topic, needles in TOPICS.items() if any(n in hay for n in needles)]


def normalize_doi(doi):
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", (doi or "").strip(), flags=re.I)
    return doi.lower().strip()


def pubmed_query():
    terms = ' OR '.join('"' + term + '"[Title/Abstract]' for terms in TOPICS.values() for term in terms)
    journals = ' OR '.join('"' + j + '"[Journal]' for j in JOURNALS)
    societies = ' OR '.join('"' + s + '"[Title]' for s in ["SEOM", "SAOM", "ESMO", "ASCO"])
    # Guideline records from society authors and the named journals; can be reviewed in config.
    return f"({terms}) AND (({journals}) OR ({societies}))"


def pubmed(days=14, max_records=160):
    today = date.today()
    since = today - timedelta(days=max(1, days))
    base = {"db": "pubmed", "tool": "ElAlmaque", "retmode": "json"}
    key = os.environ.get("NCBI_API_KEY")
    if key:
        base["api_key"] = key
    search = get(EUTIL + "esearch.fcgi", {**base, "term": pubmed_query(),
                                           "datetype": "edat", "mindate": since.isoformat(),
                                           "maxdate": today.isoformat(), "retmax": max_records,
                                           "sort": "date"}).json()
    ids = search.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []
    time.sleep(0.4)
    xml = get(EUTIL + "efetch.fcgi", {"db": "pubmed", "id": ",".join(ids), "retmode": "xml",
                                         "tool": "ElAlmaque", **({"api_key": key} if key else {})}).content
    root = ET.fromstring(xml)
    out = []
    for node in root.findall(".//PubmedArticle"):
        art = node.find(".//MedlineCitation/Article")
        if art is None:
            continue
        title = tag_text(art.find("ArticleTitle"))
        abstract = tag_text(art.find("Abstract"))
        journal = tag_text(art.find("Journal/Title"))
        pmid = tag_text(node.find(".//MedlineCitation/PMID"))
        doi = ""
        for idnode in node.findall(".//PubmedData/ArticleIdList/ArticleId"):
            if idnode.attrib.get("IdType") == "doi":
                doi = normalize_doi(tag_text(idnode))
        if not pmid or not title:
            continue
        types = [tag_text(x).lower() for x in art.findall("PublicationTypeList/PublicationType")]
        title_lower = title.lower()
        category = "Guías y protocolos" if ("guideline" in types or "practice guideline" in types or any(k in title_lower for k in GUIDE_WORDS)) else "Artículos científicos"
        # Explicit congress/supplement records are communications, never silently label them articles.
        if "congresses" in types or "meeting abstract" in types or "conference abstract" in types:
            category = "Comunicaciones científicas"
        published = node.find(".//PubMedPubDate[@PubStatus='pubmed']")
        if published is None:
            published = art.find("Journal/JournalIssue/PubDate")
        year = tag_text(published.find("Year")) if published is not None else ""
        month = tag_text(published.find("Month")) if published is not None else ""
        day = tag_text(published.find("Day")) if published is not None else ""
        published_display = " ".join(filter(None, (year, month, day)))
        topics = topic_for(title + " " + abstract)
        if not topics:
            continue
        out.append({"key": "pmid:" + pmid, "title": title, "url": "https://pubmed.ncbi.nlm.nih.gov/" + pmid + "/",
                    "publisher_url": "https://doi.org/" + doi if doi else "",
                    "doi": doi, "pmid": pmid, "source": journal or "PubMed", "society": "",
                    "category": category, "topics": topics, "date": published_display,
                    "excerpt": "", "description": "", "kind": "pubmed"})
    return out


def allowed_host(url):
    try:
        u = urlparse(url)
        return u.scheme == "https" and u.hostname in OFFICIAL_HOSTS
    except ValueError:
        return False


def classify_official(text):
    t = text.lower()
    if any(x in t for x in GUIDE_WORDS):
        return CATEGORIES[0]
    if any(x in t for x in COMMUNICATION_WORDS):
        return CATEGORIES[2]
    if any(x in t for x in NEWS_WORDS):
        return CATEGORIES[3]
    return None


def official_pages():
    records, problems = [], []
    for society, urls in OFFICIAL_PAGES.items():
        for page in urls:
            try:
                html = get(page).text
                soup = BeautifulSoup(html, "html.parser")
                found = 0
                for anchor in soup.select("a[href]"):
                    title = " ".join(anchor.get_text(" ", strip=True).split())
                    if not 22 <= len(title) <= 220:
                        continue
                    url = urljoin(page, anchor.get("href", ""))
                    if not allowed_host(url) or url.rstrip("/") == page.rstrip("/"):
                        continue
                    topics = topic_for(title)
                    category = classify_official(title)
                    if not topics or not category:
                        continue
                    # Do not mark as new based on a site's homepage: no reliable publication date.
                    # These become discovery candidates only on first encounter; a configured
                    # persistent baseline prevents re-alerting during subsequent runs.
                    clean_url = url.split("#")[0]
                    records.append({"key": "web:" + clean_url.lower(), "title": title,
                                    "url": clean_url, "publisher_url": "", "doi": "", "pmid": "",
                                    "source": society, "society": society, "category": category,
                                    "topics": topics, "date": "No verificada", "excerpt": "",
                                    "description": "Referencia oficial detectada; verificar fecha en origen.", "kind": "official"})
                    found += 1
                LOG.info("%s: %d candidate links", page, found)
            except Exception as ex:
                problems.append({"source": society, "url": page, "error": str(ex)[:180]})
                LOG.warning("Official site failed %s: %s", page, ex)
    return records, problems


def collect(days=14):
    found, issues, successes = [], [], []
    try:
        found.extend(pubmed(days=days))
        successes.append("PubMed")
    except Exception as ex:
        issues.append({"source": "PubMed", "url": "https://pubmed.ncbi.nlm.nih.gov/", "error": str(ex)[:180]})
        LOG.exception("PubMed failed")
    records, errors = official_pages()
    found.extend(records)
    issues.extend(errors)
    if len(errors) < sum(len(x) for x in OFFICIAL_PAGES.values()):
        successes.append("Sociedades (parcial o total)")
    # Prefer PubMed DOI/PMID records; dedup web link candidates.
    unique = {r["key"]: r for r in found}
    return list(unique.values()), issues, successes
