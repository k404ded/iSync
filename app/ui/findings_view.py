"""
Detailed Findings Dossier View for iSync.
Presents evidence-grounded findings with exact locations, verbatim evidence, and technical rationales.
Uses native Streamlit expanders and clean markdown without raw HTML markup.
Adheres strictly to Section 5: Detailed Findings & Grounded Evidence.
"""

import streamlit as st
from app.models.schemas import GapAnalysisReport, PriorityLevel


def render_findings_view(report: GapAnalysisReport):
    st.subheader("5. Detailed Findings & Grounded Evidence")
    st.caption("Expand any finding below to inspect the verbatim source excerpts, grounded evidence, and exact locations.")

    if not report.findings:
        st.info("No findings detected.")
        return

    # Filter controls
    col1, col2, col3 = st.columns([2, 2, 3])
    pri_filter = col1.selectbox("Filter Priority", ["All", "High", "Medium", "Low"], key="find_pri_filter")
    doc_filter = col2.selectbox("Filter Document", ["All"] + sorted(list({f.document for f in report.findings})), key="find_doc_filter")
    search_term = col3.text_input("🔍 Search Findings Text", placeholder="Filter by text, location, or change...", key="find_search")

    filtered = report.findings
    if pri_filter != "All":
        filtered = [f for f in filtered if f.priority.value == pri_filter]
    if doc_filter != "All":
        filtered = [f for f in filtered if f.document == doc_filter]
    if search_term.strip():
        q = search_term.lower()
        filtered = [
            f for f in filtered
            if q in f.software_change.lower()
            or q in f.change_summary.lower()
            or q in f.exact_location.lower()
            or q in f.affected_content.lower()
            or q in f.evidence.lower()
            or q in f.recommended_action.lower()
        ]

    if not filtered:
        st.info("No findings match the selected criteria.")
        return

    for f in filtered:
        priority_icon = "🔴" if f.priority == PriorityLevel.HIGH else ("🟡" if f.priority == PriorityLevel.MEDIUM else "🔵")
        summary_title = f.software_change or f.change_summary
        expander_title = f"{priority_icon} [{f.priority.value}] {f.finding_id} — {summary_title} ({f.document})"

        with st.expander(expander_title, expanded=(f.priority == PriorityLevel.HIGH)):
            # Metadata row
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"**Priority:** `{f.priority.value}`")
            c2.markdown(f"**Confidence:** `{f.confidence.value}`")
            c3.markdown(f"**Change Type:** `{f.change_type.value}`")
            c4.markdown(f"**Affected Document:** `{f.document}`")

            st.divider()

            st.markdown(f"**📍 Exact Location:**\n`{f.exact_location}`")

            st.markdown("**WHAT CHANGED IN SOFTWARE:**")
            st.write(f.software_change or f.change_summary)

            prev_st = f.previous_state or f.old_state
            curr_st = f.current_state or f.new_state
            if prev_st and curr_st:
                col_p, col_c = st.columns(2)
                with col_p:
                    st.markdown(f"**Previous State (Old Software):**\n`{prev_st}`")
                with col_c:
                    st.markdown(f"**Current State (Target Software):**\n`{curr_st}`")

            st.markdown("**EXISTING COURSE CONTENT:**")
            st.info(f.affected_content)

            st.markdown("**GROUNDED EVIDENCE (Verbatim Source Quote):**")
            st.warning(f"\"{f.evidence}\"")

            st.markdown("**WHY THIS IS AFFECTED:**")
            st.write(f.why_flagged)

            st.markdown("**REQUIRED AUTHOR ACTION:**")
            st.success(f.recommended_action)
