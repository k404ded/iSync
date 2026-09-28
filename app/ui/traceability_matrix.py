"""
Traceability Matrix View for iSync.
Answers Section 8 of the specification:
Software Change → Source Evidence → Existing Course Content → Exact Location → Required Action.
Provides complete end-to-end auditability from vendor delta to author task.
"""

import streamlit as st
import pandas as pd
from app.models.schemas import GapAnalysisReport


def render_traceability_matrix(report: GapAnalysisReport):
    st.subheader("8. Traceability Matrix")
    st.caption("End-to-end curriculum traceability: Software Change → Source Evidence → Existing Course Content → Exact Location → Required Action.")

    if not report.traceability_matrix:
        st.info("No traceability links generated.")
        return

    # Filter controls
    col1, col2 = st.columns([3, 4])
    doc_filter = col1.selectbox(
        "Filter by Document",
        ["All"] + sorted(list({t.document for t in report.traceability_matrix})),
        key="trace_doc_filter",
    )
    search_q = col2.text_input(
        "🔍 Search Traceability",
        placeholder="Search change, location, or action...",
        key="trace_search",
    )

    items = report.traceability_matrix
    if doc_filter != "All":
        items = [t for t in items if t.document == doc_filter]
    if search_q.strip():
        q = search_q.lower()
        items = [
            t for t in items
            if q in t.software_change.lower()
            or q in t.source_evidence.lower()
            or q in t.affected_content.lower()
            or q in t.exact_location.lower()
            or q in t.required_action.lower()
        ]

    if not items:
        st.info("No traceability rows match the search query.")
        return

    table_data = []
    for t in items:
        table_data.append({
            "Trace ID": t.trace_id,
            "Software Change": t.software_change,
            "Document": t.document,
            "Exact Location": t.exact_location,
            "Existing Course Content": t.affected_content[:120] + ("..." if len(t.affected_content) > 120 else ""),
            "Source Grounded Evidence": t.source_evidence,
            "Required Author Action": t.required_action,
            "Priority": t.priority.value,
        })

    df = pd.DataFrame(table_data)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )
