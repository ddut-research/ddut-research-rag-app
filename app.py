import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

st.set_page_config(
    page_title="North Bengal Research App",
    page_icon="📚",
    layout="wide"
)

st.title("North Bengal Research App")
st.write("A research workspace for common citizen issues in Darjeeling, Kalimpong, Jalpaiguri, and Alipurduar.")

CATEGORIES = [
    "All",
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
    "Political and Social Problems",
    "Political and Current Events"
]

if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "last_search" not in st.session_state:
    st.session_state.last_search = None
if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""
if "search_error" not in st.session_state:
    st.session_state.search_error = None
if "notes_input" not in st.session_state:
    st.session_state.notes_input = ""

def generate_answer(result):
    themes = result["themes"] or []
    tags = result["tags"] or []

    topic_line = ", ".join(themes[:3]) if themes else "the selected research themes"
    tag_line = ", ".join(tags[:3]) if tags else "the selected issue tags"

    return (
        f"The question is focused on {result['district']} and relates to {topic_line}. "
        f"Based on the selected tags, the main lens is {tag_line}. "
        f"This research should gather trusted sources, local reports, and relevant documents "
        f"before drawing conclusions."
    )

def run_search():
    if not st.session_state.question_input.strip():
        st.session_state.last_search = None
        st.session_state.last_answer = ""
        st.session_state.search_error = "Please enter a research question first."
        return

    st.session_state.search_error = None
    result = {
        "district": st.session_state.district_input,
        "question": st.session_state.question_input.strip(),
        "themes": st.session_state.themes_input,
        "tags": st.session_state.tags_input
    }
    st.session_state.last_search = result
    st.session_state.last_answer = generate_answer(result)
    st.session_state.search_history.insert(0, result)
    st.session_state.search_history = st.session_state.search_history[:50]

def delete_search(idx):
    if 0 <= idx < len(st.session_state.search_history):
        item = st.session_state.search_history.pop(idx)
        if st.session_state.last_search == item:
            st.session_state.last_search = st.session_state.search_history[0] if st.session_state.search_history else None
            st.session_state.last_answer = generate_answer(st.session_state.last_search) if st.session_state.last_search else ""

def build_report_text(result, notes, answer):
    themes = result["themes"] if result["themes"] else []
    tags = result["tags"] if result["tags"] else []
    return f"""North Bengal Research Report

District: {result['district']}
Question: {result['question']}

Answer:
{answer if answer else 'No answer generated yet.'}

Themes:
{chr(10).join(f"- {item}" for item in themes) if themes else "- None selected"}

Tags:
{chr(10).join(f"- {item}" for item in tags) if tags else "- None selected"}

Research notes:
{notes.strip() if notes.strip() else '- No notes added yet.'}
"""

def build_pdf_bytes(result, notes, answer):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    x = 20 * mm
    y = height - 20 * mm
    line_height = 7 * mm
    max_chars = 95

    def wrap_text(text, limit=max_chars):
        words = text.split()
        if not words:
            return [""]
        lines = []
        current = words[0]
        for word in words[1:]:
            test = f"{current} {word}"
            if len(test) <= limit:
                current = test
            else:
                lines.append(current)
                current = word
        lines.append(current)
        return lines

    def write_line(text, y_pos, bold=False, size=11):
        pdf.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        for line in wrap_text(text):
            if y_pos < 20 * mm:
                pdf.showPage()
                y_pos = height - 20 * mm
                pdf.setFont("Helvetica-Bold" if bold else "Helvetica", size)
            pdf.drawString(x, y_pos, line)
            y_pos -= line_height
        return y_pos

    pdf.setTitle("North Bengal Research Report")
    y = write_line("North Bengal Research Report", y, bold=True, size=16)
    y -= 4 * mm
    y = write_line(f"District: {result['district']}", y)
    y = write_line(f"Question: {result['question']}", y)
    y -= 3 * mm
    y = write_line("Answer:", y, bold=True, size=12)
    y = write_line(answer if answer else "No answer generated yet.", y)
    y -= 3 * mm
    y = write_line("Themes:", y, bold=True, size=12)
    if result["themes"]:
        for item in result["themes"]:
            y = write_line(f"- {item}", y)
    else:
        y = write_line("- None selected", y)
    y -= 3 * mm
    y = write_line("Tags:", y, bold=True, size=12)
    if result["tags"]:
        for item in result["tags"]:
            y = write_line(f"- {item}", y)
    else:
        y = write_line("- None selected", y)
    y -= 3 * mm
    y = write_line("Research Notes:", y, bold=True, size=12)
    notes_text = notes.strip() if notes.strip() else "No notes added yet."
    for paragraph in notes_text.split("\n"):
        y = write_line(paragraph if paragraph.strip() else " ", y)
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()

left, right = st.columns([1.2, 1])

with left:
    st.subheader("Research setup")

    st.selectbox(
        "Choose a district",
        ["Darjeeling", "Kalimpong", "Jalpaiguri", "Alipurduar", "All districts"],
        key="district_input"
    )

    st.text_area(
        "Enter your research question",
        placeholder="Example: How are common citizens affected by unemployment, land rights issues, water shortage, and document fraud?",
        height=140,
        key="question_input"
    )

    st.multiselect(
        "Choose research themes",
        CATEGORIES[1:-1],
        default=[
            "Unemployment and Livelihood",
            "Land Rights and Pattas",
            "Tea Garden Workers",
            "Forest Village Residents",
            "Water, Health, and Basic Services"
        ],
        key="themes_input"
    )

    st.multiselect(
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
            "Border pressure",
            "Political and Current Events"
        ],
        key="tags_input"
    )

    st.button("Search", on_click=run_search)

with right:
    st.subheader("Research preview")

    if st.session_state.search_error:
        st.warning(st.session_state.search_error)

    if st.session_state.last_search:
        result = st.session_state.last_search
        st.success("Latest search ready.")

        st.markdown(f"**District:** {result['district']}")
        st.markdown(f"**Question:** {result['question']}")
        st.markdown(f"**Answer:** {st.session_state.last_answer}")
        st.markdown(f"**Themes:** {', '.join(result['themes']) if result['themes'] else 'None selected'}")
        st.markdown(f"**Tags:** {', '.join(result['tags']) if result['tags'] else 'None selected'}")

        notes = st.session_state.notes_input
        report_text = build_report_text(result, notes, st.session_state.last_answer)
        report_df = pd.DataFrame([{
            "district": result["district"],
            "question": result["question"],
            "answer": st.session_state.last_answer,
            "themes": ", ".join(result["themes"]),
            "tags": ", ".join(result["tags"])
        }])
        pdf_bytes = build_pdf_bytes(result, notes, st.session_state.last_answer)

        st.download_button(
            label="Download text report",
            data=report_text,
            file_name="research_report.txt",
            mime="text/plain"
        )

        st.download_button(
            label="Download CSV summary",
            data=report_df.to_csv(index=False),
            file_name="research_summary.csv",
            mime="text/csv"
        )

        st.download_button(
            label="Download PDF report",
            data=pdf_bytes,
            file_name="research_report.pdf",
            mime="application/pdf"
        )

        st.info("You can download the research note, CSV summary, or PDF report and save it on your computer.")
    else:
        st.info("Enter a question and click Search to see the preview here.")

st.divider()

with st.expander("Browse saved searches"):
    browse_category = st.selectbox("Filter by category", CATEGORIES, index=0)

    filtered = []
    for item in st.session_state.search_history:
        item_text = " ".join(item.get("themes", []) + item.get("tags", [])).lower()
        if browse_category == "All" or browse_category.lower() in item_text:
            filtered.append(item)

    if filtered:
        for idx, item in enumerate(filtered):
            real_index = st.session_state.search_history.index(item)
            with st.container():
                st.markdown(f"**{item['district']}** — {item['question']}")
                st.caption(f"Themes: {', '.join(item['themes']) if item['themes'] else 'None'}")
                st.caption(f"Tags: {', '.join(item['tags']) if item['tags'] else 'None'}")
                if st.button("Delete", key=f"delete_{real_index}_{hash(item['question'])}"):
                    delete_search(real_index)
                    st.rerun()
    else:
        st.write("No saved searches match this category.")

with st.expander("Research notes"):
    st.text_area(
        "Write notes here",
        placeholder="Add observations, source links, or ideas for memorandum writing.",
        height=180,
        key="notes_input"
    )
    st.write("Notes stay in the session only for now.")

with st.expander("Recent searches"):
    if st.session_state.search_history:
        for i, item in enumerate(st.session_state.search_history, start=1):
            st.markdown(f"{i}. **{item['district']}** — {item['question']}")
    else:
        st.write("No searches yet.")

st.caption("Next step: replace the short generated answer with trusted-source research text or a source-backed summary.")
