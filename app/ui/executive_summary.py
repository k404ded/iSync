"""
Executive Summary View for iSync.
Uses native Streamlit components and markdown to present high-level metrics.
"""

import streamlit as st
from app.models.schemas import GapAnalysisReport


def render_executive_summary(report: GapAnalysisReport):
    st.subheader("1. Gap Analysis Summary")

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Software", report.software)
    m2.metric("Version Delta", f"{report.current_version} → {report.new_version}")
    m3.metric("Documents Analyzed", report.total_documents)
    m4.metric("Requiring Action", report.affected_documents_count)
    m5.metric("High Priority", report.high_priority_count)
    m6.metric("Med / Low Priority", f"{report.medium_priority_count} / {report.low_priority_count}")

    # Overall impact statement
    if report.affected_documents_count > 0:
        ratio = f"{report.affected_documents_count} of {report.total_documents}"
        st.warning(
            f"**Overall Impact:** **{ratio}** course documents require updates or review "
            f"due to changes in **{report.software} ({report.current_version} → {report.new_version})**."
        )
    else:
        st.success(
            f"**Overall Impact:** None of the {report.total_documents} uploaded documents are affected. "
            f"Existing content remains valid for **{report.software} {report.new_version}**."
        )
