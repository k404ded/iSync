"""
Impact Analyzer and Evidence Grounding Engine for iSync.
Evaluates candidate course chunks against software changes to produce verified,
evidence-grounded findings and author actions with OLD -> NEW transitions.
"""

import re
from typing import Optional, Tuple
from app.models.schemas import (
    SoftwareChange,
    ContentChunk,
    ChangeType,
    PriorityLevel,
    ConfidenceLevel,
    ImpactStatus,
    Finding,
)
from app.analysis.semantic_retriever import RetrievedCandidate


class ImpactAnalyzer:
    """Analyzes candidate matches and generates evidence-grounded findings."""

    def evaluate_candidate(
        self,
        candidate: RetrievedCandidate,
        finding_id: str,
    ) -> Optional[Finding]:
        change = candidate.change
        chunk = candidate.chunk
        text = chunk.text
        text_lower = text.lower()
        change_type = change.change_type

        # 1. Terminology Change
        if change_type == ChangeType.TERMINOLOGY_CHANGE and change.old_term:
            if change.old_term.lower() in text_lower:
                new_display = change.new_term or "the updated term"
                evidence = self._extract_verbatim_sentence(text, [change.old_term])
                why = (
                    f"The course content explicitly uses outdated terminology '{change.old_term}', "
                    f"which was officially renamed to '{new_display}' in the new release."
                )
                action = (
                    f"Update all occurrences of '{change.old_term}' to '{new_display}' in {chunk.exact_location}. "
                    f"Review surrounding explanations to ensure conceptual consistency with the updated term."
                )
                return Finding(
                    finding_id=finding_id,
                    change_id=change.change_id,
                    document=chunk.document,
                    impact_status=ImpactStatus.AFFECTED,
                    priority=PriorityLevel.HIGH,
                    confidence=ConfidenceLevel.HIGH,
                    change_type=change_type,
                    change_summary=change.title,
                    exact_location=chunk.exact_location,
                    affected_content=text,
                    evidence=evidence,
                    why_flagged=why,
                    recommended_action=action,
                    old_state=change.old_term,
                    new_state=new_display,
                    requires_manual_review=False,
                    chunk_id=chunk.chunk_id,
                )

        # 2. Deprecated or Removed Feature
        if change_type in (ChangeType.DEPRECATED_FEATURE, ChangeType.REMOVED_FEATURE):
            feature_kw = change.keywords[0].lower() if change.keywords else change.title.lower()
            if feature_kw in text_lower or (change.old_term and change.old_term.lower() in text_lower):
                evidence = self._extract_verbatim_sentence(text, [feature_kw, change.title])
                status_word = "deprecated" if change_type == ChangeType.DEPRECATED_FEATURE else "removed"
                why = (
                    f"This section instructs learners to use '{change.title}', which has been "
                    f"{status_word} in the new software version. Students following these steps will encounter missing tools or warnings."
                )
                action = (
                    f"Remove or refactor instructions referencing '{change.title}' in {chunk.exact_location}. "
                    f"Replace with the supported modern workflow or add an author advisory note."
                )
                return Finding(
                    finding_id=finding_id,
                    change_id=change.change_id,
                    document=chunk.document,
                    impact_status=ImpactStatus.AFFECTED,
                    priority=PriorityLevel.HIGH,
                    confidence=ConfidenceLevel.HIGH,
                    change_type=change_type,
                    change_summary=change.title,
                    exact_location=chunk.exact_location,
                    affected_content=text,
                    evidence=evidence,
                    why_flagged=why,
                    recommended_action=action,
                    old_state=f"Uses {status_word} {change.title}",
                    new_state="Use supported modern replacement workflow",
                    requires_manual_review=False,
                    chunk_id=chunk.chunk_id,
                )

        # 3. UI Change (Toolbar, dialog, redesigned layout)
        if change_type == ChangeType.UI_CHANGE:
            is_screenshot = chunk.has_image_or_screenshot
            # Must explicitly reference the changed UI element (e.g. "toolbar", "icon", "palette", "ribbon")
            mentions_ui_component = any(w in text_lower for w in ["toolbar", "icon", "palette", "ribbon", "dialog", "menu item", "button"])
            # Must reference the specific feature (e.g. "sketch")
            mentions_target = any(kw.lower() in text_lower for kw in change.keywords if kw.lower() in ["sketch", "toolbar", "palette", "icon"])

            if is_screenshot and ("toolbar" in text_lower or "sketch toolbar" in text_lower or chunk.image_caption):
                evidence = self._extract_verbatim_sentence(text, change.keywords)
                why = (
                    f"The course features a screenshot or figure illustrating the {change.affected_subsystem} UI. "
                    f"Because {change.description.lower()}, the visual layout in this screenshot no longer matches the live software."
                )
                action = (
                    f"Replace the screenshot at {chunk.exact_location} with a fresh capture from the new software version. "
                    f"Verify surrounding callouts and instructional text referencing button locations."
                )
                return Finding(
                    finding_id=finding_id,
                    change_id=change.change_id,
                    document=chunk.document,
                    impact_status=ImpactStatus.AFFECTED,
                    priority=PriorityLevel.HIGH,
                    confidence=ConfidenceLevel.HIGH,
                    change_type=change_type,
                    change_summary=change.title,
                    exact_location=chunk.exact_location,
                    affected_content=text,
                    evidence=evidence,
                    why_flagged=why,
                    recommended_action=action,
                    old_state="Previous UI layout and old toolbar screenshot",
                    new_state="Updated 2025 UI layout capture with refreshed icons",
                    requires_manual_review=False,
                    chunk_id=chunk.chunk_id,
                )

            # Text instructions: must mention the changed UI component specifically (e.g. "sketch toolbar")
            if mentions_ui_component and ("sketch toolbar" in text_lower or ("sketch" in text_lower and "toolbar" in text_lower)):
                evidence = self._extract_verbatim_sentence(text, ["sketch toolbar", "toolbar", "button"])
                why = (
                    f"Instructional steps direct learners to click or locate UI elements affected by '{change.title}'. "
                    f"Learners may experience confusion if button arrangement or grouping has shifted."
                )
                action = (
                    f"Review step-by-step instructions at {chunk.exact_location}. Update button names, "
                    f"ribbon paths, or visual references to match the redesigned interface."
                )
                return Finding(
                    finding_id=finding_id,
                    change_id=change.change_id,
                    document=chunk.document,
                    impact_status=ImpactStatus.AFFECTED,
                    priority=PriorityLevel.HIGH,
                    confidence=ConfidenceLevel.HIGH,
                    change_type=change_type,
                    change_summary=change.title,
                    exact_location=chunk.exact_location,
                    affected_content=text,
                    evidence=evidence,
                    why_flagged=why,
                    recommended_action=action,
                    old_state="Previous toolbar navigation instructions",
                    new_state="Updated command ribbon paths and button positions",
                    requires_manual_review=False,
                    chunk_id=chunk.chunk_id,
                )

        # 4. Workflow Change
        if change_type == ChangeType.WORKFLOW_CHANGE:
            if any(w in text_lower for w in ["step", "select", "open", "navigate", "panel", "window", "procedure"]) and any(kw.lower() in text_lower for kw in change.keywords[:4]):
                evidence = self._extract_verbatim_sentence(text, change.keywords)
                why = (
                    f"This lesson details a procedural workflow in {change.affected_subsystem}. "
                    f"The change states: '{change.description}'. The steps described in this section may direct learners to an obsolete panel location."
                )
                action = (
                    f"Validate the step sequence in {chunk.exact_location}. Update navigation directions "
                    f"to guide learners to the relocated panel/dialog."
                )
                return Finding(
                    finding_id=finding_id,
                    change_id=change.change_id,
                    document=chunk.document,
                    impact_status=ImpactStatus.AFFECTED,
                    priority=PriorityLevel.MEDIUM,
                    confidence=ConfidenceLevel.HIGH,
                    change_type=change_type,
                    change_summary=change.title,
                    exact_location=chunk.exact_location,
                    affected_content=text,
                    evidence=evidence,
                    why_flagged=why,
                    recommended_action=action,
                    old_state=change.old_workflow or "Previous procedural panel location",
                    new_state=change.new_workflow or "Updated docked panel / workflow path",
                    requires_manual_review=False,
                    chunk_id=chunk.chunk_id,
                )

        # 5. New Feature (Enhancement Opportunity)
        if change_type == ChangeType.NEW_FEATURE:
            if any(kw.lower() in text_lower for kw in ["hole", "fastener", "clearance", "wizard", "automatic"]) or change.affected_subsystem.lower() in text_lower:
                evidence = self._extract_verbatim_sentence(text, ["fastener", "hole", "clearance"])
                why = (
                    f"This section teaches fundamentals in {change.affected_subsystem}. "
                    f"The new software release introduces '{change.title}'. While the existing fundamentals remain valid, "
                    f"incorporating this new capability represents an impactful curriculum enhancement."
                )
                action = (
                    f"Add an enhancement callout or demonstration exercise in {chunk.exact_location} "
                    f"showcasing how '{change.title}' accelerates this workflow."
                )
                return Finding(
                    finding_id=finding_id,
                    change_id=change.change_id,
                    document=chunk.document,
                    impact_status=ImpactStatus.AFFECTED,
                    priority=PriorityLevel.LOW,
                    confidence=ConfidenceLevel.MEDIUM,
                    change_type=change_type,
                    change_summary=change.title,
                    exact_location=chunk.exact_location,
                    affected_content=text,
                    evidence=evidence,
                    why_flagged=why,
                    recommended_action=action,
                    old_state="Manual/traditional workflow taught",
                    new_state=f"Enhanced with new {change.title}",
                    requires_manual_review=False,
                    chunk_id=chunk.chunk_id,
                )

        # 6. Possible Impact / Fallback
        if candidate.match_type == "POSSIBLE IMPACT" and candidate.score >= 0.35:
            evidence = self._extract_verbatim_sentence(text, change.keywords)
            return Finding(
                finding_id=finding_id,
                change_id=change.change_id,
                document=chunk.document,
                impact_status=ImpactStatus.POSSIBLY_AFFECTED,
                priority=PriorityLevel.LOW,
                confidence=ConfidenceLevel.LOW,
                change_type=ChangeType.UNKNOWN_REVIEW,
                change_summary=change.title,
                exact_location=chunk.exact_location,
                affected_content=text,
                evidence=evidence,
                why_flagged=f"Domain keywords related to {change.title} detected, but evidence is insufficient for automatic classification.",
                recommended_action=f"Review section at {chunk.exact_location} to confirm whether the software change affects this exercise.",
                old_state=None,
                new_state=None,
                requires_manual_review=True,
                chunk_id=chunk.chunk_id,
            )

        return None

    def _extract_verbatim_sentence(self, text: str, search_terms: list[str]) -> str:
        """Extracts the exact sentence or clause containing the target terms."""
        clean_text = " ".join(text.split())
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", clean_text) if s.strip()]

        for s in sentences:
            s_low = s.lower()
            if any(term.lower() in s_low for term in search_terms if term):
                return s

        if len(clean_text) <= 200:
            return clean_text
        return clean_text[:180] + "..."
