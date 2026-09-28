"""
Verified Unaffected Documents View for iSync.
Explains why specific curriculum files were verified as untouched and requiring no change.
Strictly excludes current/new-version reference documents.
"""

import streamlit as st
from app.models.schemas import GapAnalysisReport


def render_not_affected_view(report: GapAnalysisReport):
    st.subheader("6. Verified Unaffected Course Material")
    st.caption("Documents inspected during analysis that contain no conflicting dependencies or obsolete workflows.")

    if not report.unaffected_documents:
        st.info("All uploaded course documents had at least one impacted section.")
        return

    for doc in report.unaffected_documents:
        with st.container(border=True):
            st.markdown(f"**🟢 {doc.document}** — *Confirmed Unaffected*")
            st.markdown(f"**Verification Reason:** {doc.non_impact_reason or 'Document was inspected thoroughly; no dependencies on the changed software capabilities were found.'}")
            st.markdown(f"**Author Directive:** `No changes required.`")
