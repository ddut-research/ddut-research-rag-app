import streamlit as st

st.set_page_config(
    page_title="North Bengal Research App",
    page_icon="📚",
    layout="wide"
)

st.title("North Bengal Research App")
st.write("A simple research app for common citizen issues in Darjeeling, Kalimpong, Jalpaiguri, and Alipurduar.")

st.subheader("Research setup")

district = st.selectbox(
    "Choose a district",
    ["Darjeeling", "Kalimpong", "Jalpaiguri", "Alipurduar", "All districts"]
)

question = st.text_input(
    "Enter your research question",
    placeholder="Example: What are the main civic and social problems affecting common people?"
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

st.subheader("Optional detail tags")
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

if st.button("Search"):
    if not question.strip():
        st.warning("Please enter a research question first.")
    else:
        st.success("Search started.")
        st.write("District:", district)
        st.write("Question:", question)
        st.write("Research themes:", ", ".join(focus_areas) if focus_areas else "None selected")
        st.write("Detail tags:", ", ".join(detail_tags) if detail_tags else "None selected")

st.divider()
st.caption("This is the first research UI version. Next we can connect search results, sources, and summaries.")
