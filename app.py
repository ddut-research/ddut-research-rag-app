import streamlit as st
import pandas as pd
from uuid import uuid4

from src.retrieval import retrieve_sources
from src.synthesis import build_citizen_summary, build_memo_brief
from src.exporters import to_txt, to_csv, to_pdf

st.set_page_config(page_title="Research Engine", page_icon="📚", layout="wide")

if "history" not in st.session_state:
    st.session_state.history = []
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "current_error" not in st.session_state:
    st.session_state.current_error = ""

st.title("Research Engine")
st.write("Source-first research for citizens and memorandum-ready drafting.")


def run_research(district, question, themes, tags):
    if not question.strip():
        return None, "Please enter a question."

    sources = retrieve_sources(
        district=district,
        question=question.strip(),
        themes=themes,
        tags=tags,
    )

    citizen = build_citizen_summary(question.strip(), district, sources)
    memo = build_memo_brief(question.strip(), district, sources)

    result = {
        "id": str(uuid4()),
        "district": district,
        "question": question.strip(),
        "themes": themes,
        "tags": tags,
        "sources": sources,
        "citizen_summary": citizen,
        "memo_brief": memo,
    }
    return result, ""


with st.form(key="research_form"):
    district = st.selectbox(
        "District",
        ["Darjeeling", "Kalimpong", "Jalpaiguri", "Alipurduar", "All districts"],
    )

    question = st.text_area(
        "Question",
        placeholder="Ask a research question here.",
    )

    themes = st.multiselect(
        "Themes",
        [
            "Unemployment and Livelihood",
            "Land Rights and Pattas",
            "Tea Garden Workers",
            "Forest Village Residents",
            "Water, Health, and Basic Services",
            "Political and Social Problems",
            "Political and Current Events",
        ],
        default=["Political and Social Problems"],
    )

    tags = st.multiselect(
        "Tags",
        [
            "Political and Current Events",
            "Public services",
            "Housing",
            "Wages",
            "Border pressure",
            "Document forgery",
        ],
        default=["Political and Current Events"],
    )

    submitted = st.form_submit_button("Research")

if submitted:
    result, error = run_research(district, question, themes, tags)

    if error:
        st.session_state.current_error = error
        st.session_state.current_result = None
    else:
        st.session_state.current_error = ""
        st.session_state.current_result = result
        st.session_state.history.insert(0, result)
        st.session_state.history = st.session_state.history[:50]

if st.session_state.current_error:
    st.error(st.session_state.current_error)

if st.session_state.current_result:
    result = st.session_state.current_result

    left, right = st.columns(2)

    with left:
        st.subheader("Citizen summary")
        st.markdown(result["citizen_summary"])

    with right:
        st.subheader("Memorandum brief")
        st.markdown(result["memo_brief"])

    st.subheader("Sources")
    source_rows = []
    for s in result["sources"]:
        source_rows.append(
            {
                "title": s.get("title", ""),
                "source_type": s.get("source_type", ""),
                "url": s.get("url", ""),
                "published": s.get("published", ""),
                "relevance": s.get("relevance", 0),
            }
        )

    df = pd.DataFrame(source_rows)
    st.dataframe(df, use_container_width=True)

    st.download_button(
        "Download citizen summary",
        data=to_txt(result["citizen_summary"]),
        file_name="citizen_summary.txt",
        mime="text/plain",
    )

    st.download_button(
        "Download memorandum brief",
        data=to_txt(result["memo_brief"]),
        file_name="memo_brief.txt",
        mime="text/plain",
    )

    st.download_button(
        "Download source table CSV",
        data=to_csv(df),
        file_name="sources.csv",
        mime="text/csv",
    )

    st.download_button(
        "Download PDF report",
        data=to_pdf(result),
        file_name="research_report.pdf",
        mime="application/pdf",
    )

with st.expander("History"):
    for item in st.session_state.history:
        st.markdown(f"**{item['district']}** — {item['question']}")
