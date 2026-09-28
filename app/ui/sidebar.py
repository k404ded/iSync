"""
Left Sidebar View for iSync.
Organizes Software Change, Course Material, Analysis execution, and Report Exports.
"""

from typing import Tuple, List, Optional
from pathlib import Path
import streamlit as st
from app.models.schemas import GapAnalysisReport
from app.export import CSVExporter, HTMLExporter, PDFExporter


def render_sidebar(
    sample_changes_text: str,
    sample_files: list,
) -> Tuple[str, str, str, str, List[any], bool, bool]:
    """
    Renders the sidebar controls.
    Returns:
        (software, current_version, new_version, change_text, course_files, run_clicked, demo_clicked)
    """
    with st.sidebar:
        st.title("⚡ iSync")
        st.markdown("**Intelligent Course Update & Gap Analysis**\n*iGETIT • Tata Technologies*")
        st.divider()

        # Section 1: Software Change
        st.subheader("1. Software Change")
        software = st.text_input("Software Name", value=st.session_state.get("sidebar_software", "SOLIDWORKS"))
        c1, c2 = st.columns(2)
        curr_ver = c1.text_input("Current Version", value=st.session_state.get("sidebar_curr_ver", "2024"))
        new_ver = c2.text_input("New Version", value=st.session_state.get("sidebar_new_ver", "2025"))

        input_mode = st.radio("Change Input Mode", ["Paste Text (Option A)", "Upload Document (Option B)"], index=0)
        change_text = ""
        uploaded_change_doc = None

        if input_mode == "Paste Text (Option A)":
            change_text = st.text_area(
                "Change Details / Release Notes",
                value=st.session_state.get("sidebar_change_text", ""),
                height=160,
                placeholder="Example:\nCHANGE 1: Sketch toolbar redesigned.\nCHANGE 2: Constraints panel moved to left tree.\nCHANGE 3: Mate Controller renamed to Kinematic Assembly Controller.\nCHANGE 4: Legacy 2D Drawing Export deprecated.\nCHANGE 5: AI-Assisted Hole Wizard introduced.",
            )
        else:
            uploaded_change_doc = st.file_uploader(
                "Upload Change / Release Document",
                type=["txt", "pdf", "docx", "csv"],
                help="Upload vendor delta notes, release guide, or change log.",
            )

        st.divider()

        # Section 2: Course Material
        st.subheader("2. Course Material")
        uploaded_courses = st.file_uploader(
            "Upload Old Training Material",
            type=["pdf", "docx", "pptx", "csv", "txt"],
            accept_multiple_files=True,
            help="Upload existing curriculum modules (PDF, Word, PowerPoint, CSV, or Text)",
        )

        active_files = uploaded_courses or []
        if active_files:
            st.markdown(f"**Loaded Files ({len(active_files)}):**")
            for f in active_files:
                st.caption(f"📄 {getattr(f, 'name', str(f))}")

        st.divider()

        # Section 3: Analysis Execution
        st.subheader("3. Analysis")
        run_clicked = st.button("⚡ ANALYZE IMPACT", type="primary", use_container_width=True)
        demo_clicked = st.button("🚀 RUN DEMO (SOLIDWORKS 2024 → 2025)", use_container_width=True)

        st.divider()

        # Section 4: Export (rendered when report exists in session state)
        if st.session_state.get("report"):
            st.subheader("4. Export Report")
            rep: GapAnalysisReport = st.session_state["report"]

            csv_bytes = CSVExporter.export(rep)
            st.download_button(
                "📥 Export CSV",
                data=csv_bytes,
                file_name=f"iSync_{rep.software}_{rep.new_version}_{rep.report_id}.csv",
                mime="text/csv",
                use_container_width=True,
            )

            html_str = HTMLExporter.export(rep)
            st.download_button(
                "📥 Export HTML Report",
                data=html_str,
                file_name=f"iSync_{rep.software}_{rep.new_version}_{rep.report_id}.html",
                mime="text/html",
                use_container_width=True,
            )

            pdf_bytes = PDFExporter.export(rep)
            st.download_button(
                "📥 Export PDF Dossier",
                data=pdf_bytes,
                file_name=f"iSync_{rep.software}_{rep.new_version}_{rep.report_id}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    # If change doc uploaded, parse its text
    final_change_text = change_text
    if uploaded_change_doc:
        from app.parsers import DocumentLoader
        loader = DocumentLoader()
        chunks = loader.parse_document(uploaded_change_doc, uploaded_change_doc.name)
        file_text = "\n".join([c.text for c in chunks])
        final_change_text = f"{final_change_text}\n{file_text}".strip()

    return software, curr_ver, new_ver, final_change_text, active_files, run_clicked, demo_clicked
