"""
Tests for Hybrid Semantic & Lexical Retriever.
"""

from app.models.schemas import SoftwareChange, ContentChunk, ChangeType
from app.analysis.semantic_retriever import SemanticRetriever


def test_retriever_direct_match():
    change = SoftwareChange(
        change_id="CHG-001",
        title="Mate Controller renamed to Kinematic Assembly Controller",
        change_type=ChangeType.TERMINOLOGY_CHANGE,
        description="Mate Controller has been renamed to Kinematic Assembly Controller.",
        affected_subsystem="Assembly",
        keywords=["Mate Controller", "Kinematic Assembly Controller", "Controller"],
        old_term="Mate Controller",
        new_term="Kinematic Assembly Controller",
    )

    chunks = [
        ContentChunk(
            chunk_id="c1",
            document="Advanced_Parts_Assembly.docx",
            doc_type="docx",
            module="Module 4",
            lesson="Lesson 1",
            text="In this lesson, we study kinematic positions. Select the Mate Controller from the tree.",
        ),
        ContentChunk(
            chunk_id="c2",
            document="Sketching_Fundamentals.pdf",
            doc_type="pdf",
            module="Module 2",
            lesson="Lesson 1",
            text="Draw a circle by selecting the center point and dragging outward.",
        ),
    ]

    retriever = SemanticRetriever(threshold=0.25)
    candidates = retriever.retrieve_candidates(change, chunks)

    assert len(candidates) == 1
    assert candidates[0].chunk.chunk_id == "c1"
    assert candidates[0].match_type == "DIRECT MATCH"
    assert candidates[0].score >= 0.8


def test_retriever_semantic_match():
    change = SoftwareChange(
        change_id="CHG-002",
        title="Constraints panel moved into docked Left FeatureManager tree",
        change_type=ChangeType.WORKFLOW_CHANGE,
        description="Constraints panel moved from floating window directly into docked tree.",
        affected_subsystem="Assembly Constraints",
        keywords=["Constraints panel", "floating window", "docked tree", "FeatureManager"],
    )

    chunks = [
        ContentChunk(
            chunk_id="c1",
            document="Constraints_and_Mates.pptx",
            doc_type="pptx",
            module="Module 3",
            lesson="Lesson 2",
            text="Open the Constraints window and select the Constraints panel to define relationships.",
        ),
        ContentChunk(
            chunk_id="c2",
            document="Intro.pdf",
            doc_type="pdf",
            module="Module 1",
            lesson="Lesson 1",
            text="Welcome to the CAD software tutorial course overview.",
        ),
    ]

    retriever = SemanticRetriever(threshold=0.20)
    candidates = retriever.retrieve_candidates(change, chunks)

    assert len(candidates) >= 1
    assert candidates[0].chunk.chunk_id == "c1"
    assert candidates[0].chunk.document == "Constraints_and_Mates.pptx"


def test_retriever_unrelated_material():
    change = SoftwareChange(
        change_id="CHG-003",
        title="Thermal analysis mesh refinement updated",
        change_type=ChangeType.PERFORMANCE_TECHNICAL,
        description="Finite element mesh solver optimized for thermal boundary simulations.",
        affected_subsystem="Simulation / FEA",
        keywords=["Thermal analysis", "mesh refinement", "FEA"],
    )

    chunks = [
        ContentChunk(
            chunk_id="c1",
            document="Sketching_Fundamentals.pdf",
            doc_type="pdf",
            module="Module 2",
            lesson="Lesson 1",
            text="Click Line tool and sketch line on the front plane.",
        ),
    ]

    retriever = SemanticRetriever(threshold=0.25)
    candidates = retriever.retrieve_candidates(change, chunks)
    assert len(candidates) == 0
