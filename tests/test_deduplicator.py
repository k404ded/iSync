"""
Tests for FindingDeduplicator.
"""

from app.models.schemas import (
    Finding,
    ChangeType,
    PriorityLevel,
    ConfidenceLevel,
    ImpactStatus,
)
from app.analysis.deduplicator import FindingDeduplicator


def test_deduplicator_removes_duplicate_locations():
    f1 = Finding(
        finding_id="TEMP-01",
        change_id="CHG-001",
        document="Advanced_Parts_Assembly.docx",
        impact_status=ImpactStatus.AFFECTED,
        priority=PriorityLevel.HIGH,
        confidence=ConfidenceLevel.HIGH,
        change_type=ChangeType.TERMINOLOGY_CHANGE,
        change_summary="Mate Controller renamed",
        exact_location="Advanced_Parts_Assembly.docx → Lesson 1 → Page 1",
        affected_content="Select Mate Controller from the tree.",
        evidence="Select Mate Controller",
        why_flagged="Outdated term",
        recommended_action="Update to Kinematic Assembly Controller",
    )
    # Duplicate with slightly different wording on the same page
    f2 = Finding(
        finding_id="TEMP-02",
        change_id="CHG-001",
        document="Advanced_Parts_Assembly.docx",
        impact_status=ImpactStatus.AFFECTED,
        priority=PriorityLevel.HIGH,
        confidence=ConfidenceLevel.HIGH,
        change_type=ChangeType.TERMINOLOGY_CHANGE,
        change_summary="Mate Controller renamed",
        exact_location="Advanced_Parts_Assembly.docx → Lesson 1 → Page 1",
        affected_content="Mate Controller provides precise joint angles.",
        evidence="Mate Controller provides",
        why_flagged="Outdated term",
        recommended_action="Update to Kinematic Assembly Controller",
    )

    # Different document under the same change
    f3 = Finding(
        finding_id="TEMP-03",
        change_id="CHG-001",
        document="Feature_Glossary_Index.csv",
        impact_status=ImpactStatus.AFFECTED,
        priority=PriorityLevel.HIGH,
        confidence=ConfidenceLevel.HIGH,
        change_type=ChangeType.TERMINOLOGY_CHANGE,
        change_summary="Mate Controller renamed",
        exact_location="Feature_Glossary_Index.csv → Row 14",
        affected_content="Mate Controller glossary row",
        evidence="Mate Controller",
        why_flagged="Outdated term",
        recommended_action="Update to Kinematic Assembly Controller",
    )

    deduped = FindingDeduplicator.deduplicate([f1, f2, f3])
    assert len(deduped) == 2
    assert deduped[0].finding_id == "FND-001"
    assert deduped[0].document == "Advanced_Parts_Assembly.docx"
    assert deduped[1].finding_id == "FND-002"
    assert deduped[1].document == "Feature_Glossary_Index.csv"


def test_deduplicator_preserves_screenshot_vs_text():
    f_screenshot = Finding(
        finding_id="TEMP-01",
        change_id="CHG-UI",
        document="Sketching_Fundamentals.pdf",
        impact_status=ImpactStatus.AFFECTED,
        priority=PriorityLevel.HIGH,
        confidence=ConfidenceLevel.HIGH,
        change_type=ChangeType.UI_CHANGE,
        change_summary="Sketch toolbar redesigned",
        exact_location="Sketching_Fundamentals.pdf → Page 3",
        affected_content="Figure 2-1 Sketch toolbar screenshot",
        evidence="Figure 2-1: Sketch Toolbar Layout",
        why_flagged="Outdated screenshot",
        recommended_action="Replace the screenshot with updated 2025 capture",
    )
    f_text = Finding(
        finding_id="TEMP-02",
        change_id="CHG-UI",
        document="Sketching_Fundamentals.pdf",
        impact_status=ImpactStatus.AFFECTED,
        priority=PriorityLevel.HIGH,
        confidence=ConfidenceLevel.HIGH,
        change_type=ChangeType.UI_CHANGE,
        change_summary="Sketch toolbar redesigned",
        exact_location="Sketching_Fundamentals.pdf → Page 3",
        affected_content="Click the Sketch toolbar button on top",
        evidence="Sketch toolbar button",
        why_flagged="Outdated instruction",
        recommended_action="Review step-by-step instructions and ribbon path",
    )

    deduped = FindingDeduplicator.deduplicate([f_screenshot, f_text])
    assert len(deduped) == 2
    assert deduped[0].finding_id == "FND-001"
    assert deduped[1].finding_id == "FND-002"
