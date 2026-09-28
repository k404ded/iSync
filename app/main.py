"""
iSync — Intelligent Course Update & Gap Analysis Agent
Production Web Application for iGETIT Content Architecture (Tata Technologies).
Rebuilt from the ground up for zero-hallucination, evidence-grounded course maintenance.
"""

import sys
from pathlib import Path
import streamlit as st

# Setup python path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from app.config import SAMPLE_DATA_DIR, SAMPLE_COURSES_DIR
from app.parsers import DocumentLoader
from app.analysis import GapAnalysisPipeline
from app.models.schemas import GapAnalysisReport
from app.ui import (
    APP_CSS,
    render_sidebar,
    render_executive_summary,
    render_impact_map,
    render_action_plan,
    render_findings_view,
    render_not_affected_view,
)

# Page configuration
st.set_page_config(
    page_title="iSync — Intelligent Course Update Gap Analysis Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject safe top-level stylesheet
st.markdown(APP_CSS, unsafe_allow_html=True)


def load_demo_fixtures():
    """Loads sample files and change notes for the 1-click benchmark demo."""
    if not (SAMPLE_DATA_DIR / "changes.txt").exists():
        from scripts.generate_sample_data import generate_sample_files
        generate_sample_files(root_dir)

    raw_changes = (SAMPLE_DATA_DIR / "changes.txt").read_text(encoding="utf-8")
    sample_files = list(SAMPLE_COURSES_DIR.glob("*.*"))
    return raw_changes, sample_files


def execute_pipeline(
    software: str,
    curr_ver: str,
    new_ver: str,
    change_text: str,
    course_files: list,
) -> GapAnalysisReport:
    """Executes the analysis pipeline using the exact same code for both custom and demo runs."""
    progress_bar = st.progress(0)
    status_box = st.empty()

    def update_progress(step: int, msg: str):
        progress_bar.progress(step / 5.0)
        status_box.markdown(f"**Stage {step}/5:** {msg}")

    # Parse all uploaded/selected files
    update_progress(1, f"Parsing and indexing {len(course_files)} course documents...")
    loader = DocumentLoader()
    all_chunks = loader.parse_multiple(course_files)
    doc_names = list(dict.fromkeys([getattr(f, "name", None) or Path(f).name for f in course_files]))

    pipeline = GapAnalysisPipeline()
    report = pipeline.run(
        software=software,
        current_version=curr_ver,
        new_version=new_ver,
        change_text=change_text,
        all_chunks=all_chunks,
        all_document_names=doc_names,
        progress_cb=update_progress,
    )

    progress_bar.progress(1.0)
    status_box.success(f"✓ Analysis complete! Processed {report.total_documents} documents; identified {len(report.findings)} verified findings.")
    return report


# Top Branding Header
st.title("⚡ iSync — Intelligent Course Update Gap Analysis Agent")
st.caption("AI-Powered Curriculum Maintenance & Delta Detection • iGETIT Architecture • Tata Technologies")
st.divider()

# Prepare demo fixture references
demo_changes, demo_files = load_demo_fixtures()

# Render Left Sidebar
software, curr_ver, new_ver, change_text, course_files, run_clicked, demo_clicked = render_sidebar(
    sample_changes_text=demo_changes,
    sample_files=demo_files,
)

# Demo Mode Trigger
if demo_clicked:
    st.session_state["sidebar_software"] = "SOLIDWORKS"
    st.session_state["sidebar_curr_ver"] = "2024"
    st.session_state["sidebar_new_ver"] = "2025"
    st.session_state["sidebar_change_text"] = demo_changes

    with st.spinner("Executing end-to-end benchmark analysis on SOLIDWORKS 2024 → 2025..."):
        report = execute_pipeline(
            software="SOLIDWORKS",
            curr_ver="2024",
            new_ver="2025",
            change_text=demo_changes,
            course_files=demo_files,
        )
        st.session_state["report"] = report
        st.rerun()

# Real Analysis Trigger with Input Validation
elif run_clicked:
    # Validation per Section 19
    errors = []
    if not software.strip():
        errors.append("Please enter the **Software Name**.")
    if not curr_ver.strip():
        errors.append("Please enter the **Current Version**.")
    if not new_ver.strip():
        errors.append("Please enter the **New Version**.")
    if not change_text.strip():
        errors.append("Please provide **Software Change Details** (paste text or upload a release notes document).")
    if not course_files:
        errors.append("Please upload at least one **Course Document** (PDF, DOCX, PPTX, CSV, or TXT).")

    if errors:
        for err in errors:
            st.error(err)
    else:
        with st.spinner("Analyzing curriculum gap impact..."):
            report = execute_pipeline(
                software=software,
                curr_ver=curr_ver,
                new_ver=new_ver,
                change_text=change_text,
                course_files=course_files,
            )
            st.session_state["report"] = report
            st.rerun()

# Main Screen: Empty State OR Results
if not st.session_state.get("report"):
    st.markdown("### Intelligent Course Update Analysis")
    st.markdown(
        """
        Identify exactly which training materials must change when your engineering software is updated.
        
        **How to use iSync:**
        1. **Specify the software and version transition** in the sidebar (e.g. *SOLIDWORKS 2024 → 2025*).
        2. **Provide the software change details** by pasting release notes or uploading documentation.
        3. **Upload your existing course material** (PDF, DOCX, PPTX, CSV, or TXT).
        4. Click **`⚡ ANALYZE IMPACT`** to generate the evidence-grounded action plan.
        """
    )

    st.info(
        "💡 **Quick Evaluation:** Click **'🚀 RUN DEMO (SOLIDWORKS 2024 → 2025)'** in the sidebar to run the complete analysis pipeline on sample CAD course modules."
    )
else:
    report: GapAnalysisReport = st.session_state["report"]

    # 1. Executive Summary
    render_executive_summary(report)
    st.divider()

    # 2. Document Impact Map
    render_impact_map(report)
    st.divider()

    # 3. Author Action Plan
    render_action_plan(report)
    st.divider()

    # 4. Detailed Findings Dossier
    render_findings_view(report)
    st.divider()

    # 5. Verified Unaffected Course Material
    render_not_affected_view(report)
