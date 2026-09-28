"""
Tests for CSV, HTML, and PDF Exporters.
"""

from app.models.schemas import (
    GapAnalysisReport,
    DocumentSummary,
    Finding,
    ActionItem,
    ChangeType,
    PriorityLevel,
    ConfidenceLevel,
    ImpactStatus,
)
from app.export import CSVExporter, HTMLExporter, PDFExporter


def create_sample_report() -> GapAnalysisReport:
    doc_sum = DocumentSummary(
        document="Advanced_Parts_Assembly.docx",
        status=ImpactStatus.AFFECTED,
        highest_priority=PriorityLevel.HIGH,
        affected_locations_count=1,
        change_types=[ChangeType.TERMINOLOGY_CHANGE],
        action_summary="Update Mate Controller to Kinematic Assembly Controller",
    )
    unaffected = DocumentSummary(
        document="Intro.pdf",
        status=ImpactStatus.NOT_AFFECTED,
        highest_priority=None,
        affected_locations_count=0,
        change_types=[],
        action_summary="No changes required",
        non_impact_reason="No dependencies found",
    )
    finding = Finding(
        finding_id="FND-001",
        change_id="CHG-001",
        document="Advanced_Parts_Assembly.docx",
        impact_status=ImpactStatus.AFFECTED,
        priority=PriorityLevel.HIGH,
        confidence=ConfidenceLevel.HIGH,
        change_type=ChangeType.TERMINOLOGY_CHANGE,
        change_summary="Mate Controller renamed to Kinematic Assembly Controller",
        exact_location="Advanced_Parts_Assembly.docx → Module 4 → Lesson 1 → Page 1",
        affected_content="Select the Mate Controller from the tree.",
        evidence="Select the Mate Controller from the tree.",
        why_flagged="Outdated terminology",
        recommended_action="Update Mate Controller to Kinematic Assembly Controller",
        old_state="Mate Controller",
        new_state="Kinematic Assembly Controller",
    )
    action = ActionItem(
        action_id="ACT-001",
        document="Advanced_Parts_Assembly.docx",
        action_type="Replace Terminology",
        priority=PriorityLevel.HIGH,
        exact_location="Advanced_Parts_Assembly.docx → Module 4 → Lesson 1 → Page 1",
        change_title="Mate Controller renamed",
        instructions="Update Mate Controller to Kinematic Assembly Controller",
        old_state="Mate Controller",
        new_state="Kinematic Assembly Controller",
        finding_ref="FND-001",
    )

    return GapAnalysisReport(
        report_id="RPT-TEST-001",
        software="SOLIDWORKS",
        current_version="2024",
        new_version="2025",
        total_documents=2,
        affected_documents_count=1,
        high_priority_count=1,
        medium_priority_count=0,
        low_priority_count=0,
        document_summaries=[doc_sum, unaffected],
        findings=[finding],
        action_plan=[action],
        unaffected_documents=[unaffected],
    )


def test_csv_exporter():
    report = create_sample_report()
    csv_bytes = CSVExporter.export(report)
    assert len(csv_bytes) > 0
    csv_text = csv_bytes.decode("utf-8")
    assert "FND-001" in csv_text
    assert "Advanced_Parts_Assembly.docx" in csv_text
    assert "Mate Controller" in csv_text


def test_html_exporter():
    report = create_sample_report()
    html_text = HTMLExporter.export(report)
    assert "<!DOCTYPE html>" in html_text
    assert "SOLIDWORKS" in html_text
    assert "2024" in html_text and "2025" in html_text
    assert "FND-001" in html_text
    assert "Kinematic Assembly Controller" in html_text
    assert "Intro.pdf" in html_text


def test_pdf_exporter():
    report = create_sample_report()
    pdf_bytes = PDFExporter.export(report)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")
