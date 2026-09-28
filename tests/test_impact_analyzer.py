"""
Tests for Impact Analyzer and Evidence Grounding Engine.
"""

from app.models.schemas import (
    SoftwareChange,
    ContentChunk,
    ChangeType,
    PriorityLevel,
    ConfidenceLevel,
    ImpactStatus,
)
from app.analysis.semantic_retriever import RetrievedCandidate
from app.analysis.impact_analyzer import ImpactAnalyzer


def test_impact_analyzer_terminology_change():
    analyzer = ImpactAnalyzer()
    change = SoftwareChange(
        change_id="CHG-001",
        title="Mate Controller renamed to Kinematic Assembly Controller",
        change_type=ChangeType.TERMINOLOGY_CHANGE,
        description="Mate Controller has been renamed to Kinematic Assembly Controller.",
        affected_subsystem="Assembly",
        keywords=["Mate Controller", "Kinematic Assembly Controller"],
        old_term="Mate Controller",
        new_term="Kinematic Assembly Controller",
    )
    chunk = ContentChunk(
        chunk_id="chk_1",
        document="Advanced_Parts_Assembly.docx",
        doc_type="docx",
        module="Module 4",
        lesson="Lesson 1",
        text="In this lesson, select the Mate Controller from the tree to record positions.",
    )
    candidate = RetrievedCandidate(
        change=change,
        chunk=chunk,
        match_type="DIRECT MATCH",
        score=0.95,
        reasons=["Direct match on obsolete terminology"],
    )

    finding = analyzer.evaluate_candidate(candidate, "FND-001")
    assert finding is not None
    assert finding.finding_id == "FND-001"
    assert finding.priority == PriorityLevel.HIGH
    assert finding.confidence == ConfidenceLevel.HIGH
    assert finding.old_state == "Mate Controller"
    assert finding.new_state == "Kinematic Assembly Controller"
    assert "Mate Controller" in finding.evidence


def test_impact_analyzer_deprecated_feature():
    analyzer = ImpactAnalyzer()
    change = SoftwareChange(
        change_id="CHG-002",
        title="Legacy 2D Drawing Export deprecated",
        change_type=ChangeType.DEPRECATED_FEATURE,
        description="Legacy 2D Drawing Export has been deprecated in favor of native MBD workflows.",
        affected_subsystem="Drafting",
        keywords=["Legacy 2D Drawing Export", "MBD"],
    )
    chunk = ContentChunk(
        chunk_id="chk_2",
        document="Advanced_Parts_Assembly.docx",
        doc_type="docx",
        module="Module 4",
        lesson="Lesson 2",
        text="To export traditional draft sheets, run the Legacy 2D Drawing Export utility from the Tools menu.",
    )
    candidate = RetrievedCandidate(
        change=change,
        chunk=chunk,
        match_type="DIRECT MATCH",
        score=0.92,
        reasons=["Direct match on feature keyword"],
    )

    finding = analyzer.evaluate_candidate(candidate, "FND-002")
    assert finding is not None
    assert finding.priority == PriorityLevel.HIGH
    assert finding.change_type == ChangeType.DEPRECATED_FEATURE
    assert "Legacy 2D Drawing Export" in finding.evidence
    assert "deprecated" in finding.why_flagged.lower()


def test_impact_analyzer_ui_screenshot_change():
    analyzer = ImpactAnalyzer()
    change = SoftwareChange(
        change_id="CHG-003",
        title="Sketch toolbar redesigned with updated icon arrangement",
        change_type=ChangeType.UI_CHANGE,
        description="Sketch toolbar redesigned with updated icon arrangement and unified palette grouping.",
        affected_subsystem="Sketching",
        keywords=["Sketch toolbar", "icon arrangement", "palette"],
    )
    chunk = ContentChunk(
        chunk_id="chk_3",
        document="Sketching_Fundamentals.pdf",
        doc_type="pdf",
        module="Module 2",
        lesson="Lesson 3",
        page=3,
        text="Figure 2-1 shows the standard Sketch toolbar layout for drawing entities.",
        has_image_or_screenshot=True,
        image_caption="Figure 2-1: Sketch Toolbar Layout",
    )
    candidate = RetrievedCandidate(
        change=change,
        chunk=chunk,
        match_type="DIRECT MATCH",
        score=0.90,
        reasons=["Visual diagram corresponding to redesigned UI"],
    )

    finding = analyzer.evaluate_candidate(candidate, "FND-003")
    assert finding is not None
    assert finding.priority == PriorityLevel.HIGH
    assert finding.change_type == ChangeType.UI_CHANGE
    assert "screenshot" in finding.recommended_action.lower()


def test_impact_analyzer_workflow_change():
    analyzer = ImpactAnalyzer()
    change = SoftwareChange(
        change_id="CHG-004",
        title="Constraints panel moved into docked Left FeatureManager design tree",
        change_type=ChangeType.WORKFLOW_CHANGE,
        description="Constraints panel moved from floating window into docked tree.",
        affected_subsystem="Assembly Constraints",
        keywords=["Constraints panel", "floating window", "docked tree"],
        old_workflow="Constraints panel in floating window",
        new_workflow="Constraints panel in docked Left FeatureManager tree",
    )
    chunk = ContentChunk(
        chunk_id="chk_4",
        document="Constraints_and_Mates.pptx",
        doc_type="pptx",
        lesson="Lesson 2",
        slide=2,
        text="Step 1: Open the Constraints window and select the Constraints panel to define relationships.",
    )
    candidate = RetrievedCandidate(
        change=change,
        chunk=chunk,
        match_type="DIRECT MATCH",
        score=0.85,
        reasons=["Procedural match"],
    )

    finding = analyzer.evaluate_candidate(candidate, "FND-004")
    assert finding is not None
    assert finding.priority == PriorityLevel.MEDIUM
    assert finding.change_type == ChangeType.WORKFLOW_CHANGE
    assert finding.old_state == "Constraints panel in floating window"
