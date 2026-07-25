import streamlit as st

st.set_page_config(
    page_title="North Bengal Research App",
    page_icon="📚",
    layout="wide"
)

st.title("North Bengal Research App")
st.write("A research workspace for common citizen issues in Darjeeling, Kalimpong, Jalpaiguri, and Alipurduar.")

if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "last_search" not in st.session_state:
    st.session_state.last_search = None

left, right = st.columns([1.2, 1])

with left:
    st.subheader("Research setup")

    district = st.selectbox(
        "Choose a district",
        ["Darjeeling", "Kalimpong", "Jalpaiguri", "Alipurduar", "All districts"]
    )

    question = st.text_area(
        "Enter your research question",
        placeholder="Example: How are common citizens affected by unemployment, land rights issues, water shortage, and document fraud?",
        height=140
    )

    focus_areas = st.multiselect(
        "Choose research themes",
        [
            "Unemployment and Livelihood",
            "Land Rights and Pattas",
            "Tea Garden Workers",
            "Generational Tea Garden Residents",
            "Forest Village Residents",
            "Migration and Trafficking",
            "Water, Health, and Basic Services",
            "Identity, Documents, and Fraud",
            "Borders, Security, and Infiltration",
            "Property and Land Disputes",
            "Social and Civic Problems",
            "History",
            "Culture",
            "Language",
            "Demographics",
            "Socio-economics",
            "Land Issues",
            "Agitations and Movements",
            "Political and Social Problems"
        ],
        default=[
            "Unemployment and Livelihood",
            "Land Rights and Pattas",
            "Tea Garden Workers",
            "Forest Village Residents",
            "Water, Health, and Basic Services"
        ]
    )

    detail_tags = st.multiselect(
        "Add specific issue tags",
        [
            "Human trafficking",
            "Land mafia",
            "Document forgery",
            "ID forgery",
            "Drinking water",
            "Housing",
            "Employment loss",
            "Wages",
            "Public services",
            "Border pressure"
        ]
    )

    search_clicked = st.button("Search")

    if search_clicked:
        if not question.strip():
            st.warning("Please enter a research question first.")
        else:
            result = {
                "district": district,
                "question": question.strip(),
                "themes": focus_areas,
                "tags": detail_tags
            }
            st.session_state.last_search = result
            st.session_state.search_history.insert(0, result)
            st.session_state.search_history = st.session_state.search_history[:5]

with right:
    st.subheader("Research preview")

    if st.session_state.last_search:
        result = st.session_state.last_search
        st.success("Latest search ready.")

        st.markdown(f"**District:** {result['district']}")
        st.markdown(f"**Question:** {result['question']}")
        st.markdown(
            f"**Themes:** {', '.join(result['themes']) if result['themes'] else 'None selected'}"
        )
        st.markdown(
            f"**Tags:** {', '.join(result['tags']) if result['tags'] else 'None selected'}"
        )

        st.info("This panel will later show a short summary, source links, and research findings.")
    else:
        st.info("Enter a question and click Search to see the preview here.")

st.divider()

with st.expander("Research notes"):
    notes = st.text_area(
        "Write notes here",
        placeholder="Add observations, source links, or ideas for memorandum writing.",
        height=180
    )
    st.write("Notes stay in the session only for now.")

with st.expander("Source list preview"):
    st.markdown(
        """
        - Government reports
        - News reports
        - Academic papers
        - District-level documents
        - Community and field reports
        """
    )

with st.expander("Recent searches"):
    if st.session_state.search_history:
        for i, item in enumerate(st.session_state.search_history, start=1):
            st.markdown(
                f"{i}. **{item['district']}** — {item['question']}"
            )
    else:
        st.write("No searches yet.")

st.caption("Next step: connect the search button to structured summaries and source generation.")
