import streamlit as st

st.set_page_config(
    page_title="North Bengal Research App",
    page_icon="📚",
    layout="wide"
)

st.title("North Bengal Research App")
st.write("A research workspace for common citizen issues in Darjeeling, Kalimpong, Jalpaiguri, and Alipurduar.")

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

with right:
    st.subheader("Research preview")

    if search_clicked:
        if not question.strip():
            st.warning("Please enter a research question first.")
        else:
            st.success("Search started.")
            st.markdown(f"**District:** {district}")
            st.markdown(f"**Question:** {question}")
            st.markdown(f"**Themes:** {', '.join(focus_areas) if focus_areas else 'None selected'}")
            st.markdown(f"**Tags:** {', '.join(detail_tags) if detail_tags else 'None selected'}")
            st.info("This area will later show summaries, sources, and research findings.")
    else:
        st.info("Enter a question and click Search to see the preview here.")

st.divider()

with st.expander("Research notes"):
    notes = st.text_area(
        "Write notes here",
        placeholder="Add observations, source links, or ideas for memorandum writing.",
        height=180
    )
    st.write("Notes saved in the app session will be added later.")

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

st.caption("First layout version of the research app. Next we can add source links and structured summaries.")
