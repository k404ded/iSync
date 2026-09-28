"""
Tests for iSync Schema Models.
"""

from app.models.schemas import (
    ChangeType,
    PriorityLevel,
    ConfidenceLevel,
    ImpactStatus,
    SoftwareChange,
    ContentChunk,
    Finding,
    ActionItem,
    DocumentSummary,
    GapAnalysisReport,
)


def test_software_change_schema():
    chg = SoftwareChange(
        change_id="CHG-001",
        title="Sketch toolbar redesigned",
        change_type=ChangeType.UI_CHANGE,
        description="Redesigned toolbar layout and palette",
        affected_subsystem="Sketching",
        keywords=["Sketch", "Toolbar"],
    )
    assert chg.change_id == "CHG-001"
    assert chg.change_type == ChangeType.UI_CHANGE
    assert chg.affected_subsystem == "Sketching"


def test_content_chunk_exact_location():
    chunk = ContentChunk(
        chunk_id="c1",
        document="Sketching_Fundamentals.pdf",
        doc_type="pdf",
        module="Module 2",
        lesson="Lesson 3",
        section="Sketch Environment",
        page=14,
        text="Open Sketch and click toolbar.",
    )
    loc = chunk.exact_location
    assert "Sketching_Fundamentals.pdf" in loc
    assert "Module 2" in loc
    assert "Lesson 3" in loc
    assert "Page 14" in loc


def test_gap_analysis_report_metrics():
    doc_sum = DocumentSummary(
        document="Test.pdf",
        status=ImpactStatus.AFFECTED,
        highest_priority=PriorityLevel.HIGH,
        affected_locations_count=1,
        change_types=[ChangeType.UI_CHANGE],
        action_summary="Replace screenshot",
    )
    unaffected = DocumentSummary(
        document="Intro.pdf",
        status=ImpactStatus.NOT_AFFECTED,
        highest_priority=None,
        affected_locations_count=0,
        change_types=[],
        action_summary="No changes required",
        non_impact_reason="No dependencies",
    )
    finding = Finding(
        finding_id="FND-001",
        change_id="CHG-001",
        document="Test.pdf",
        impact_status=ImpactStatus.AFFECTED,
        priority=PriorityLevel.HIGH,
        confidence=ConfidenceLevel.HIGH,
        change_type=ChangeType.UI_CHANGE,
        change_summary="Sketch toolbar redesigned",
        exact_location="Test.pdf → Page 14",
        affected_content="Old toolbar text",
        evidence="Old toolbar text",
        why_flagged="UI redesign",
        recommended_action="Replace screenshot",
    )

    report = GapAnalysisReport(
        report_id="RPT-TEST",
        software="SOLIDWORKS",
        current_version="2024",
        new_version="2025",
        total_documents=2,
        affected_documents_count=1,
        high_priority_count=1,
        document_summaries=[doc_sum, unaffected],
        findings=[finding],
        unaffected_documents=[unaffected],
    )

    assert report.total_documents == 2
    assert report.affected_documents_count == 1
    assert len(report.unaffected_documents) == 1
