"""
Software Change Inventory View for iSync.
Presents the extracted software changes as a structured inventory per Section 1 of the specification:
Change ID, Software area/module, Feature or workflow, Previous state, New/current state, Change type, Source location, Confidence.
"""

import streamlit as st
import pandas as pd
from app.models.schemas import GapAnalysisReport


def render_change_inventory(report: GapAnalysisReport):
    st.subheader("2. Software Change Inventory")
    st.caption("Structured inventory of all verified vendor release changes, deltas, and deprecations.")

    if not report.changes:
        st.info("No software changes identified in the provided release input.")
        return

    # Filter controls
    col1, col2 = st.columns([3, 4])
    type_filter = col1.selectbox(
        "Filter Change Type",
        ["All"] + sorted(list({c.change_type.value for c in report.changes})),
        key="inv_type_filter",
    )
    search_term = col2.text_input(
        "🔍 Search Change Inventory",
        placeholder="Filter by feature, keyword, or subsystem...",
        key="inv_search",
    )

    filtered = report.changes
    if type_filter != "All":
        filtered = [c for c in filtered if c.change_type.value == type_filter]
    if search_term.strip():
        q = search_term.lower()
        filtered = [
            c for c in filtered
            if q in c.title.lower()
            or q in c.description.lower()
            or q in c.software_area.lower()
            or q in c.feature_workflow.lower()
            or any(q in kw.lower() for kw in c.keywords)
        ]

    if not filtered:
        st.info("No changes match the selected criteria.")
        return

    table_data = []
    for c in filtered:
        table_data.append({
            "Change ID": c.change_id,
            "Software Area": c.software_area,
            "Feature / Workflow": c.feature_workflow or c.title,
            "Previous State (Old)": c.previous_state or c.old_term or "—",
            "Current State (New)": c.current_state or c.new_term or "—",
            "Change Type": c.change_type.value,
            "Source Location": c.source_location,
            "Confidence": c.confidence.value,
        })

    df = pd.DataFrame(table_data)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )
