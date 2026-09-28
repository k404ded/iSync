"""
Document Impact Map View for iSync.
Presents the document-level impact overview with filtering and search.
"""

import streamlit as st
import pandas as pd
from app.models.schemas import GapAnalysisReport, ImpactStatus, PriorityLevel


def render_impact_map(report: GapAnalysisReport):
    st.subheader("2. Document Impact Map")
    st.caption("Document-level status indicating whether each training module requires updates, review, or no change.")

    # Filter controls
    f_col1, f_col2, f_col3 = st.columns([2, 2, 3])
    status_filter = f_col1.selectbox("Filter Status", ["All", "Affected", "Not Affected"])
    priority_filter = f_col2.selectbox("Filter Priority", ["All", "High", "Medium", "Low"])
    search_q = f_col3.text_input("🔍 Search Document or Action", placeholder="Type document name, feature, or action...")

    summaries = report.document_summaries

    if status_filter != "All":
        summaries = [s for s in summaries if s.status.value == status_filter]
    if priority_filter != "All":
        summaries = [s for s in summaries if s.highest_priority and s.highest_priority.value == priority_filter]
    if search_q.strip():
        q = search_q.lower()
        summaries = [
            s for s in summaries
            if q in s.document.lower()
            or q in s.action_summary.lower()
            or any(q in t.value.lower() for t in s.change_types)
        ]

    if not summaries:
        st.info("No documents match the selected filters.")
        return

    table_data = []
    for s in summaries:
        pri_str = s.highest_priority.value if s.highest_priority else "—"
        types_str = ", ".join([t.value for t in s.change_types]) if s.change_types else "None"
        table_data.append({
            "Document": s.document,
            "Impact Status": s.status.value,
            "Highest Priority": pri_str,
            "Affected Locations": s.affected_locations_count,
            "Change Categories": types_str,
            "Required Author Action": s.action_summary,
        })

    df = pd.DataFrame(table_data)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )
