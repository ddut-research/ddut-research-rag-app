import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import streamlit as st

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

TRUSTED_SOURCES = [
    "gov.in",
    "nic.in",
    "india.gov.in",
    "thehindu.com",
    "indianexpress.com",
    "bbc.com",
    "telegraphindia.com",
    "reuters.com",
    "timesofindia.indiatimes.com",
    "business-standard.com",
    "millenniumpost.in",
]

def _search_queries(district, question, themes, tags):
    base = [district, question]
    if themes:
        base.append(" ".join(themes[:3]))
    if tags:
        base.append(" ".join(tags[:3]))
    return " ".join(base).strip()

def _parse_page(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        text = " ".join(soup.get_text(" ", strip=True).split())
        title = soup.title.get_text(strip=True) if soup.title else url
        return title, text[:6000]
    except Exception:
        return url, ""

def _fake_search_results(query):
    # Replace this with real search API or site-specific search later.
    return []

@st.cache_data(ttl=3600)
def retrieve_sources(district, question, themes, tags):
    query = _search_queries(district, question, themes, tags)
    results = []

    urls = _fake_search_results(query)

    for url in urls:
        title, text = _parse_page(url)
        if not text:
            continue
        results.append({
            "title": title,
            "url": url,
            "source_type": "trusted_web",
            "published": "",
            "content": text,
            "relevance": 1,
        })

    if not results:
        results.append({
            "title": "No sources retrieved yet",
            "url": "",
            "source_type": "placeholder",
            "published": "",
            "content": "Retrieval engine not connected to live search yet.",
            "relevance": 0,
        })

    return results
