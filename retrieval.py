import re
import hashlib
from urllib.parse import quote_plus, urlparse

import requests
import streamlit as st
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )
}

TRUSTED_DOMAINS = [
    "gov.in",
    "nic.in",
    "india.gov.in",
    "reuters.com",
    "bbc.com",
    "thehindu.com",
    "indianexpress.com",
    "hindustantimes.com",
    "telegraphindia.com",
    "business-standard.com",
]

SEARCH_ENDPOINTS = [
    "https://duckduckgo.com/html/?q={query}",
    "https://www.google.com/search?q={query}",
]

def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()

def _domain_allowed(url: str) -> bool:
    domain = urlparse(url).netloc.lower()
    return any(domain.endswith(d) for d in TRUSTED_DOMAINS)

def _make_query(district: str, question: str, themes: list[str], tags: list[str]) -> str:
    parts = [district, question]
    parts.extend(themes or [])
    parts.extend(tags or [])
    return _normalize_text(" ".join(parts))

def _hash_key(*parts) -> str:
    raw = "||".join([str(p) for p in parts])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

def _extract_visible_text(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    text = soup.get_text(" ", strip=True)
    return _normalize_text(title), _normalize_text(text)

def _extract_candidate_links(search_html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(search_html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/l/?") or href.startswith("http"):
            links.append(href)
    return links

def _clean_duckduckgo_url(url: str) -> str:
    if url.startswith("/l/?"):
        return url
    return url

def _search_web(query: str, max_results: int = 8) -> list[str]:
    candidates = []
    for endpoint in SEARCH_ENDPOINTS:
        try:
            url = endpoint.format(query=quote_plus(query))
            resp = requests.get(url, headers=HEADERS, timeout=12)
            resp.raise_for_status()
            found = _extract_candidate_links(resp.text, url)
            candidates.extend(found)
            if len(candidates) >= max_results * 3:
                break
        except requests.RequestException:
            continue

    cleaned = []
    seen = set()
    for url in candidates:
        url = _clean_duckduckgo_url(url)
        if not url.startswith("http"):
            continue
        if url in seen:
            continue
        seen.add(url)
        if _domain_allowed(url):
            cleaned.append(url)
        if len(cleaned) >= max_results:
            break
    return cleaned

def _fetch_page(url: str) -> dict:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        title, text = _extract_visible_text(resp.text)
        return {
            "url": url,
            "title": title or url,
            "content": text[:12000],
            "status": "ok",
        }
    except requests.RequestException as e:
        return {
            "url": url,
            "title": url,
            "content": "",
            "status": f"error: {e.__class__.__name__}",
        }

def _score_source(url: str, title: str, content: str, question: str, themes: list[str], tags: list[str]) -> float:
    score = 0.0
    text = f"{title} {content}".lower()
    needles = [question] + (themes or []) + (tags or [])
    for needle in needles:
        n = needle.lower().strip()
        if not n:
            continue
        if n in text:
            score += 2.0
        else:
            score += sum(0.25 for token in n.split() if token in text)

    domain = urlparse(url).netloc.lower()
    if any(domain.endswith(d) for d in TRUSTED_DOMAINS):
        score += 3.0
    if "gov.in" in domain or "nic.in" in domain or "india.gov.in" in domain:
        score += 2.0
    return score

@st.cache_data(ttl=3600, show_spinner=False)
def retrieve_sources(district: str, question: str, themes: list[str] | None = None, tags: list[str] | None = None) -> list[dict]:
    themes = themes or []
    tags = tags or []
    query = _make_query(district, question, themes, tags)
    urls = _search_web(query, max_results=8)

    sources = []
    seen = set()

    for url in urls:
        if url in seen:
            continue
        seen.add(url)

        page = _fetch_page(url)
        if page["status"] != "ok" or not page["content"]:
            continue

        relevance = _score_source(
            url=page["url"],
            title=page["title"],
            content=page["content"],
            question=question,
            themes=themes,
            tags=tags,
        )

        sources.append({
            "id": _hash_key(url, page["title"]),
            "title": page["title"],
            "url": page["url"],
            "source_type": "web",
            "published": "",
            "domain": urlparse(url).netloc.lower(),
            "content": page["content"],
            "relevance": relevance,
        })

    sources.sort(key=lambda x: x["relevance"], reverse=True)

    if not sources:
        sources.append({
            "id": _hash_key(query, "placeholder"),
            "title": "No trusted sources retrieved",
            "url": "",
            "source_type": "placeholder",
            "published": "",
            "domain": "",
            "content": "No trusted sources matched this query.",
            "relevance": 0.0,
        })

    return sources
