"""
Current-State Reference Documents View for iSync.
Presents the vendor release notes, change guides, or new-version reference documents
used to establish the ground-truth target state.
"""

import streamlit as st
from app.models.schemas import GapAnalysisReport


def render_reference_documents_view(report: GapAnalysisReport):
    st.subheader("7. Current-State Reference Documents")
    st.caption("Documents provided as the current/new-version source of truth to establish the target software state.")

    if not report.reference_documents:
        st.info("No separate reference documentation files were provided. Analysis was performed using parsed change release notes.")
        return

    for doc in report.reference_documents:
        with st.container(border=True):
            st.markdown(f"**🔵 {doc.document}** — *Current-State Reference*")
            st.markdown(f"**Role:** {doc.action_summary or 'Current-state reference used to establish the target software state.'}")
            st.caption("This document serves as the vendor benchmark delta and is excluded from curriculum maintenance alerts.")
