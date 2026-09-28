"""
Tests for ChangeExtractor.
"""

from app.analysis.change_extractor import ChangeExtractor
from app.models.schemas import ChangeType


def test_change_extraction():
    raw_text = """SOLIDWORKS 2025 Release Notes & Software Delta:

CHANGE 1:
Sketch toolbar redesigned with updated icon arrangement and unified palette grouping.

CHANGE 2:
Constraints panel moved from the floating window directly into the docked Left FeatureManager design tree.

CHANGE 3:
Mate Controller has been renamed to Kinematic Assembly Controller to reflect modern multi-body simulation standards.

CHANGE 4:
Legacy 2D Drawing Export has been deprecated in favor of native MBD workflows.

CHANGE 5:
AI-Assisted Hole Wizard introduced for automatic fastener sizing and intelligent hole positioning."""

    extractor = ChangeExtractor()
    changes = extractor.extract_changes(raw_text, "SOLIDWORKS", "2024", "2025")

    assert len(changes) == 5
    types = [c.change_type for c in changes]
    assert ChangeType.UI_CHANGE in types
    assert ChangeType.WORKFLOW_CHANGE in types
    assert ChangeType.TERMINOLOGY_CHANGE in types
    assert ChangeType.DEPRECATED_FEATURE in types
    assert ChangeType.NEW_FEATURE in types

    term_chg = next(c for c in changes if c.change_type == ChangeType.TERMINOLOGY_CHANGE)
    assert term_chg.old_term == "Mate Controller"
    assert "Kinematic Assembly Controller" in (term_chg.new_term or "")
