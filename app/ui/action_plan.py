"""
Author Action Plan View for iSync.
Answers the central question: "What exactly do I need to change?"
Presents grouped, concrete tasks per document with exact locations and OLD -> NEW comparisons.
"""

import streamlit as st
from app.models.schemas import GapAnalysisReport, PriorityLevel


def render_action_plan(report: GapAnalysisReport):
    st.subheader("3. Author Action Plan")
    st.caption("Actionable course maintenance checklist for authors and curriculum developers.")

    if not report.action_plan:
        st.info("No actionable updates required across the analyzed course materials.")
        return

    # Group action items by document
    doc_plan: dict[str, list] = {}
    for item in report.action_plan:
        doc_plan.setdefault(item.document, []).append(item)

    doc_counter = 1
    for doc_name, items in doc_plan.items():
        st.markdown(f"### {doc_counter}. {doc_name}")
        doc_counter += 1

        for act in items:
            badge_icon = "🔴" if act.priority == PriorityLevel.HIGH else ("🟡" if act.priority == PriorityLevel.MEDIUM else "🔵")
            with st.container(border=True):
                st.markdown(f"**{badge_icon} [{act.priority.value} Priority] {act.action_type}** — *{act.change_title}*")
                st.markdown(f"**📍 Location:** `{act.exact_location}`")

                if act.old_state and act.new_state:
                    col_old, col_new = st.columns(2)
                    with col_old:
                        st.markdown(f"**FROM (Previous State):**\n`{act.old_state}`")
                    with col_new:
                        st.markdown(f"**TO (Target State):**\n`{act.new_state}`")

                st.markdown(f"**👉 Action Required:** {act.instructions}")
