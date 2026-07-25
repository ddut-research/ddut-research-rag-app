import streamlit as st
import pandas as pd
from io import BytesIO
from uuid import uuid4
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
    q = result["question"].lower()
    district = result["district"]
    themes = result["themes"] or []
    tags = result["tags"] or []

    if any(term in q for term in ["political", "politics", "situation", "current"]):
        return f"""
### Current situation

Trusted reports indicate that Darjeeling politics is shaped by the long-running Gorkhaland or statehood issue, competition among hill parties, and growing attention to everyday governance issues such as roads, drinking water, healthcare, and tea garden wages.

### Main actors

Recent coverage shows continued competition among the BJP, BGPM, GJM-linked groups, and other hill-based political forces. The GTA and the idea of a permanent political solution remain central to the political debate.

### What is changing

The political mood in the hills is not only about identity anymore. Reporting from 2026 also suggests that voters and parties are paying more attention to delivery, development, corruption, and who can actually improve daily life in the hills.

### Research takeaway

If you are researching this issue, the best summary is that Darjeeling is in a phase of active political competition where identity-based demands, development concerns, and the search for a lasting settlement all overlap.
""".strip()

    topic_line = ", ".join(themes[:3]) if themes else "the selected research themes"
    tag_line = ", ".join(tags[:3]) if tags else "the selected issue tags"

    return f"""
### Research focus

The question is focused on **{district}** and relates to {topic_line}. Based on the selected tags, the main lens is {tag_line}.

### What this suggests

This question should be researched using trusted sources, local reports, official records, and issue-specific documents before drawing conclusions.

### Research takeaway

The main task is to collect evidence, compare reliable reports, and build a clear summary that answers the question directly.
""".strip()

def run_search():
    if not st.session_state.question_input.strip():
        st.session_state.last_search = None
        st.session_state.last_answer = ""
        st.session_state.search_error = "Please enter a research question first."
        return

    st.session_state.search_error = None
    result = {
        "id": str(uuid4()),
        "district": st.session_state.district_input,
        "question": st.session_state.question_input.strip(),
        "themes": st.session_state.themes_input,
        "tags": st.session_state.tags_input,
    }
    st.session_state.last_search = result
    st.session_state.last_answer = generate_answer(result)
    st.session_state.search_history.insert(0, result)
    st.session_state.search_history = st.session_state.search_history[:50]

def delete_search(search_id):
    st.session_state.search_history = [
        item for item in st.session_state.search_history
        if item["id"] != search_id
    ]
    if st.session_state.last_search and st.session_state.last_search["id"] == search_id:
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
        key="district_input",
    )

    st.text_area(
        "Enter your research question",
        placeholder="Example: What is the current political situation of Darjeeling?",
        height=140,
        key="question_input",
    )

    st.multiselect(
        "Choose research themes",
        CATEGORIES[1:-1],
        default=["Political and Social Problems"],
        key="themes_input",
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
            "Political and Current Events",
        ],
        default=["Political and Current Events"],
        key="tags_input",
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

        st.markdown("### Answer")
        st.markdown(st.session_state.last_answer)

        st.markdown(f"**Themes:** {', '.join(result['themes']) if result['themes'] else 'None selected'}")
        st.markdown(f"**Tags:** {', '.join(result['tags']) if result['tags'] else 'None selected'}")

        notes = st.session_state.notes_input
        report_text = build_report_text(result, notes, st.session_state.last_answer)
        report_df = pd.DataFrame([{
            "district": result["district"],
            "question": result["question"],
            "answer": st.session_state.last_answer,
            "themes": ", ".join(result["themes"]),
            "tags": ", ".join(result["tags"]),
        }])
        pdf_bytes = build_pdf_bytes(result, notes, st.session_state.last_answer)

        st.download_button(
            label="Download text report",
            data=report_text,
            file_name="research_report.txt",
            mime="text/plain",
        )

        st.download_button(
            label="Download CSV summary",
            data=report_df.to_csv(index=False),
            file_name="research_summary.csv",
            mime="text/csv",
        )

        st.download_button(
            label="Download PDF report",
            data=pdf_bytes,
            file_name="research_report.pdf",
            mime="application/pdf",
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
        for item in filtered:
            st.markdown(f"**{item['district']}** — {item['question']}")
            st.caption(f"Themes: {', '.join(item['themes']) if item['themes'] else 'None'}")
            st.caption(f"Tags: {', '.join(item['tags']) if item['tags'] else 'None'}")
            if st.button("Delete", key=f"delete_{item['id']}"):
                delete_search(item["id"])
                st.rerun()
    else:
        st.write("No saved searches match this category.")

with st.expander("Research notes"):
    st.text_area(
        "Write notes here",
        placeholder="Add observations, source links, or ideas for memorandum writing.",
        height=180,
        key="notes_input",
    )
    st.write("Notes stay in the session only for now.")

with st.expander("Recent searches"):
    if st.session_state.search_history:
        for i, item in enumerate(st.session_state.search_history, start=1):
            st.markdown(f"{i}. **{item['district']}** — {item['question']}")
    else:
        st.write("No searches yet.")

st.caption("Next step: connect the answer section to live trusted-source retrieval for richer research summaries.")
