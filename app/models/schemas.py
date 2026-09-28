"""
iSync Production Schema Definitions.
Strictly typed data structures for changes, document chunks, findings, action plans, and gap reports.
Follows the evidence-grounded output contract.
"""

from __future__ import annotations
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ChangeType(str, Enum):
    NEW_FEATURE = "New Feature"
    FEATURE_CHANGE = "Feature Change"
    UI_CHANGE = "UI Change"
    WORKFLOW_CHANGE = "Workflow Change"
    TERMINOLOGY_CHANGE = "Terminology Change"
    DEPRECATED_FEATURE = "Deprecated Feature"
    REMOVED_FEATURE = "Removed Feature"
    MODIFIED_BEHAVIOR = "Modified Behavior"
    PERFORMANCE_TECHNICAL = "Performance/Technical Change"
    COMPATIBILITY_CHANGE = "Compatibility Change"
    DOCUMENTATION_CHANGE = "Documentation Change"
    UNKNOWN_REVIEW = "Unknown / Requires Review"


class PriorityLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class ConfidenceLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class ImpactStatus(str, Enum):
    AFFECTED = "Affected"
    POSSIBLY_AFFECTED = "Possibly Affected"
    NOT_AFFECTED = "Not Affected"


class SoftwareChange(BaseModel):
    change_id: str = Field(..., description="Unique change ID (e.g. CHG-001)")
    title: str = Field(..., description="Short title of the change")
    change_type: ChangeType = Field(..., description="Standardized category of change")
    description: str = Field(..., description="Full description of the software change")
    affected_subsystem: str = Field("General", description="Module or subsystem (e.g. Sketching, Assembly)")
    old_term: Optional[str] = Field(None, description="Previous term or command name if renamed")
    new_term: Optional[str] = Field(None, description="New term or command name")
    old_workflow: Optional[str] = Field(None, description="Previous sequence of steps if altered")
    new_workflow: Optional[str] = Field(None, description="Updated sequence of steps")
    keywords: List[str] = Field(default_factory=list, description="Keywords for lexical and semantic lookup")


class ContentChunk(BaseModel):
    chunk_id: str
    document: str
    doc_type: str  # "pdf", "docx", "pptx", "csv", "txt"
    module: Optional[str] = None
    lesson: Optional[str] = None
    section: Optional[str] = None
    page: Optional[int] = None
    slide: Optional[int] = None
    row: Optional[int] = None
    heading: Optional[str] = None
    text: str
    has_image_or_screenshot: bool = False
    image_caption: Optional[str] = None
    order_index: int = 0
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def exact_location(self) -> str:
        parts = [self.document]
        if self.module:
            parts.append(self.module)
        if self.lesson:
            parts.append(self.lesson)
        if self.section and self.section != self.lesson:
            parts.append(self.section)
        if self.heading and self.heading not in (self.section, self.lesson, self.module):
            parts.append(self.heading)

        if self.page is not None:
            parts.append(f"Page {self.page}")
        elif self.slide is not None:
            parts.append(f"Slide {self.slide}")
        elif self.row is not None:
            parts.append(f"Row {self.row}")

        return " → ".join(parts) if len(parts) > 1 else f"{self.document} (Location details unavailable from source)"


class Finding(BaseModel):
    finding_id: str
    change_id: str
    document: str
    impact_status: ImpactStatus = ImpactStatus.AFFECTED
    priority: PriorityLevel
    confidence: ConfidenceLevel
    change_type: ChangeType
    change_summary: str
    exact_location: str
    affected_content: str
    evidence: str
    why_flagged: str
    recommended_action: str
    old_state: Optional[str] = None
    new_state: Optional[str] = None
    requires_manual_review: bool = False
    chunk_id: str = ""


class ActionItem(BaseModel):
    action_id: str
    document: str
    change_title: str
    action_type: str  # "Replace Screenshot", "Replace Terminology", "Update Workflow", "Remove Deprecated Step", "Add Enhancement"
    exact_location: str
    old_state: Optional[str] = None
    new_state: Optional[str] = None
    instructions: str
    priority: PriorityLevel


class DocumentSummary(BaseModel):
    document: str
    status: ImpactStatus
    highest_priority: Optional[PriorityLevel] = None
    affected_locations_count: int = 0
    change_types: List[ChangeType] = Field(default_factory=list)
    action_summary: str = "No action required"
    non_impact_reason: Optional[str] = None
    findings: List[Finding] = Field(default_factory=list)


class GapAnalysisReport(BaseModel):
    report_id: str
    software: str
    current_version: str
    new_version: str
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_documents: int = 0
    affected_documents_count: int = 0
    high_priority_count: int = 0
    medium_priority_count: int = 0
    low_priority_count: int = 0
    changes: List[SoftwareChange] = Field(default_factory=list)
    document_summaries: List[DocumentSummary] = Field(default_factory=list)
    findings: List[Finding] = Field(default_factory=list)
    action_plan: List[ActionItem] = Field(default_factory=list)
    unaffected_documents: List[DocumentSummary] = Field(default_factory=list)
