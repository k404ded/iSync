"""
Comprehensive Acceptance Criteria Tests.
Directly implements tests for:
- Section 37: Acceptance Test 1 (Terminology change)
- Section 38: Acceptance Test 2 (Deprecated feature)
- Section 39: Acceptance Test 3 (UI change)
- End-to-End Pipeline on all 5 sample files
"""

from pathlib import Path
from app.config import SAMPLE_COURSES_DIR, SAMPLE_DATA_DIR
from app.parsers import DocumentLoader
from app.analysis import GapAnalysisPipeline
from app.models.schemas import ChangeType, PriorityLevel, ImpactStatus


def test_acceptance_scenario_1_terminology_change():
    """
    Scenario 37:
    CHANGE: "Mate Controller has been renamed to Kinematic Assembly Controller."
    DOCUMENTS: Advanced_Parts_Assembly.docx, Feature_Glossary_Index.csv, Sketching_Fundamentals.pdf, Introduction_and_Overview.pdf
    EXPECTED:
    - Advanced_Parts_Assembly.docx: Affected, Terminology Change, exact locations, Old: Mate Controller, New: Kinematic Assembly Controller
    - Feature_Glossary_Index.csv: Affected, Terminology Change, exact location, action
    - Sketching_Fundamentals.pdf: NOT affected
    - Introduction_and_Overview.pdf: NOT affected
    """
    loader = DocumentLoader()
    doc_paths = [
        SAMPLE_COURSES_DIR / "Advanced_Parts_Assembly.docx",
        SAMPLE_COURSES_DIR / "Feature_Glossary_Index.csv",
        SAMPLE_COURSES_DIR / "Sketching_Fundamentals.pdf",
        SAMPLE_COURSES_DIR / "Introduction_and_Overview.pdf",
    ]
    all_chunks = loader.parse_multiple(doc_paths)
    doc_names = [p.name for p in doc_paths]

    change_text = "Mate Controller has been renamed to Kinematic Assembly Controller to reflect modern multi-body simulation standards."

    pipeline = GapAnalysisPipeline()
    report = pipeline.run(
        software="SOLIDWORKS",
        current_version="2024",
        new_version="2025",
        change_text=change_text,
        all_chunks=all_chunks,
        all_document_names=doc_names,
    )

    doc_map = {d.document: d for d in report.document_summaries}

    # Advanced_Parts_Assembly.docx must be affected
    assert doc_map["Advanced_Parts_Assembly.docx"].status == ImpactStatus.AFFECTED
    assert ChangeType.TERMINOLOGY_CHANGE in doc_map["Advanced_Parts_Assembly.docx"].change_types
    assert doc_map["Advanced_Parts_Assembly.docx"].highest_priority == PriorityLevel.HIGH

    # Feature_Glossary_Index.csv must be affected
    assert doc_map["Feature_Glossary_Index.csv"].status == ImpactStatus.AFFECTED
    assert ChangeType.TERMINOLOGY_CHANGE in doc_map["Feature_Glossary_Index.csv"].change_types
    assert doc_map["Feature_Glossary_Index.csv"].highest_priority == PriorityLevel.HIGH

    # Sketching_Fundamentals.pdf and Introduction_and_Overview.pdf must NOT be affected
    assert doc_map["Sketching_Fundamentals.pdf"].status == ImpactStatus.NOT_AFFECTED
    assert doc_map["Introduction_and_Overview.pdf"].status == ImpactStatus.NOT_AFFECTED

    # Verify findings contain old and new terminology
    term_findings = [f for f in report.findings if f.change_type == ChangeType.TERMINOLOGY_CHANGE]
    assert len(term_findings) >= 2
    for f in term_findings:
        assert f.old_state == "Mate Controller"
        assert "Kinematic Assembly Controller" in f.new_state
        assert "Mate Controller" in f.evidence


def test_acceptance_scenario_2_deprecated_feature():
    """
    Scenario 38:
    CHANGE: "Legacy 2D Drawing Export has been deprecated in favor of native MBD workflows."
    EXPECTED:
    - Advanced_Parts_Assembly.docx: Affected, High Priority, Deprecated Feature, exact location, old/new instructions
    """
    loader = DocumentLoader()
    doc_paths = [
        SAMPLE_COURSES_DIR / "Advanced_Parts_Assembly.docx",
        SAMPLE_COURSES_DIR / "Introduction_and_Overview.pdf",
    ]
    all_chunks = loader.parse_multiple(doc_paths)
    doc_names = [p.name for p in doc_paths]

    change_text = "Legacy 2D Drawing Export has been deprecated in favor of native MBD workflows."

    pipeline = GapAnalysisPipeline()
    report = pipeline.run(
        software="SOLIDWORKS",
        current_version="2024",
        new_version="2025",
        change_text=change_text,
        all_chunks=all_chunks,
        all_document_names=doc_names,
    )

    doc_map = {d.document: d for d in report.document_summaries}
    assert doc_map["Advanced_Parts_Assembly.docx"].status == ImpactStatus.AFFECTED
    assert ChangeType.DEPRECATED_FEATURE in doc_map["Advanced_Parts_Assembly.docx"].change_types
    assert doc_map["Advanced_Parts_Assembly.docx"].highest_priority == PriorityLevel.HIGH

    dep_findings = [f for f in report.findings if f.change_type == ChangeType.DEPRECATED_FEATURE]
    assert len(dep_findings) >= 1
    assert "Legacy 2D Drawing Export" in dep_findings[0].evidence
    assert dep_findings[0].priority == PriorityLevel.HIGH


def test_acceptance_scenario_3_ui_change():
    """
    Scenario 39:
    CHANGE: "Sketch toolbar redesigned with updated icon arrangement."
    EXPECTED:
    - Sketching_Fundamentals.pdf: Affected, UI Change, replace screenshot action
    """
    loader = DocumentLoader()
    doc_paths = [
        SAMPLE_COURSES_DIR / "Sketching_Fundamentals.pdf",
        SAMPLE_COURSES_DIR / "Introduction_and_Overview.pdf",
    ]
    all_chunks = loader.parse_multiple(doc_paths)
    doc_names = [p.name for p in doc_paths]

    change_text = "Sketch toolbar redesigned with updated icon arrangement and unified palette grouping."

    pipeline = GapAnalysisPipeline()
    report = pipeline.run(
        software="SOLIDWORKS",
        current_version="2024",
        new_version="2025",
        change_text=change_text,
        all_chunks=all_chunks,
        all_document_names=doc_names,
    )

    doc_map = {d.document: d for d in report.document_summaries}
    assert doc_map["Sketching_Fundamentals.pdf"].status == ImpactStatus.AFFECTED
    assert ChangeType.UI_CHANGE in doc_map["Sketching_Fundamentals.pdf"].change_types

    ui_findings = [f for f in report.findings if f.change_type == ChangeType.UI_CHANGE]
    assert len(ui_findings) >= 1
    assert any("screenshot" in f.recommended_action.lower() for f in ui_findings)


def test_full_pipeline_5_sample_files():
    """
    End-to-End Test on full 5-document curriculum benchmark.
    """
    raw_changes = (SAMPLE_DATA_DIR / "changes.txt").read_text(encoding="utf-8")
    course_files = list(SAMPLE_COURSES_DIR.glob("*.*"))

    loader = DocumentLoader()
    all_chunks = loader.parse_multiple(course_files)
    doc_names = [f.name for f in course_files]

    pipeline = GapAnalysisPipeline()
    report = pipeline.run(
        software="SOLIDWORKS",
        current_version="2024",
        new_version="2025",
        change_text=raw_changes,
        all_chunks=all_chunks,
        all_document_names=doc_names,
    )

    assert report.total_documents == 5
    assert report.affected_documents_count == 4
    assert len(report.unaffected_documents) == 1
    assert report.unaffected_documents[0].document == "Introduction_and_Overview.pdf"
    assert report.high_priority_count >= 4
    assert len(report.findings) >= 6
    assert len(report.action_plan) >= 6

    # Verify no raw HTML in findings, summaries, or actions
    for f in report.findings:
        assert "<div" not in f.why_flagged
        assert "<div" not in f.recommended_action
        assert "<span" not in f.why_flagged
    for a in report.action_plan:
        assert "<div" not in a.instructions
