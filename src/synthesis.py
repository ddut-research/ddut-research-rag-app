from __future__ import annotations

from typing import List, Dict


def _top_sources(sources: List[Dict], limit: int = 5) -> List[Dict]:
    return sorted(sources, key=lambda x: x.get("relevance", 0), reverse=True)[:limit]


def _clean_text(text: str) -> str:
    return " ".join((text or "").split()).strip()


def _pick_evidence_snippets(sources: List[Dict], limit: int = 3) -> List[str]:
    snippets = []
    for source in _top_sources(sources, limit=limit):
        content = _clean_text(source.get("content", ""))
        if not content:
            continue
        snippet = content[:280]
        if len(content) > 280:
            snippet += "..."
        title = source.get("title", "Untitled source")
        snippets.append(f"- {title}: {snippet}")
    return snippets


def build_citizen_summary(question: str, district: str, sources: List[Dict]) -> str:
    top = _top_sources(sources, limit=3)
    snippets = _pick_evidence_snippets(top, limit=3)

    if not top or (len(top) == 1 and top[0].get("source_type") == "placeholder"):
        return (
            f"### Citizen summary\n\n"
            f"No trusted sources were found for **{district}** on the question: "
            f"“{question}”.\n\n"
            f"Please refine the question or add a better source list."
        )

    source_lines = []
    for src in top:
        title = src.get("title", "Untitled source")
        url = src.get("url", "")
        if url:
            source_lines.append(f"- [{title}]({url})")
        else:
            source_lines.append(f"- {title}")

    return (
        f"### Citizen summary\n\n"
        f"For **{district}**, the available evidence suggests the following about "
        f"“{question}”:\n\n"
        f"{chr(10).join(snippets) if snippets else '- Evidence was limited.'}\n\n"
        f"**Most relevant sources:**\n"
        f"{chr(10).join(source_lines)}"
    )


def build_memo_brief(question: str, district: str, sources: List[Dict]) -> str:
    top = _top_sources(sources, limit=5)

    if not top or (len(top) == 1 and top[0].get("source_type") == "placeholder"):
        return (
            f"### Memorandum brief\n\n"
            f"**Subject:** {question}\n\n"
            f"**District:** {district}\n\n"
            f"**Finding:** No trusted sources were retrieved.\n\n"
            f"**Action:** Re-run retrieval with a revised query or add authoritative sources."
        )

    rows = []
    for src in top:
        title = src.get("title", "Untitled source")
        url = src.get("url", "")
        relevance = src.get("relevance", 0)
        domain = src.get("domain", "")
        if url:
            rows.append(f"- **{title}** ({domain}, score: {relevance:.2f}) — [{url}]({url})")
        else:
            rows.append(f"- **{title}** ({domain}, score: {relevance:.2f})")

    evidence = _pick_evidence_snippets(top, limit=5)

    return (
        f"### Memorandum brief\n\n"
        f"**Subject:** {question}\n\n"
        f"**District:** {district}\n\n"
        f"**Assessment:** The retrieval layer returned a ranked set of sources. "
        f"The strongest items are listed below.\n\n"
        f"**Evidence summary:**\n"
        f"{chr(10).join(evidence) if evidence else '- No extractable evidence snippets.'}\n\n"
        f"**Source ranking:**\n"
        f"{chr(10).join(rows)}\n\n"
        f"**Note:** This brief is generated from retrieved web evidence and should "
        f"be validated against primary sources before final use."
    )
