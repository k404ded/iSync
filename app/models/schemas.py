"""
iSync Production Schema Definitions.
Strictly typed data structures for software changes, document chunks, findings, action plans, and gap reports.
Follows the evidence-grounded output contract and 8-stage analysis architecture.
"""

from __future__ import annotations
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ChangeType(str, Enum):
    UI_CHANGE = "UI Change"
    WORKFLOW_CHANGE = "Workflow Change"
    FEATURE_ADDED = "Feature Added"
    FEATURE_REMOVED = "Feature Removed"
    REMOVED_FEATURE = "Removed Feature"
    FEATURE_MODIFIED = "Feature Modified"
    COMMAND_CHANGE = "Command Change"
    MENU_NAVIGATION_CHANGE = "Menu/Navigation Change"
    TERMINOLOGY_CHANGE = "Terminology Change"
    DEPRECATED_FEATURE = "Deprecated Feature"
    CONFIGURATION_CHANGE = "Configuration Change"
    COMPATIBILITY_CHANGE = "Compatibility Change"
    PERFORMANCE_CHANGE = "Performance Change"
    PERFORMANCE_TECHNICAL = "Performance/Technical Change"
    NEW_FEATURE = "New Feature"
    FEATURE_CHANGE = "Feature Change"
    MODIFIED_BEHAVIOR = "Modified Behavior"
    DOCUMENTATION_CHANGE = "Documentation Change"
    OTHER = "Other"
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
    POTENTIALLY_AFFECTED = "Potentially Affected"
    POSSIBLY_AFFECTED = "Potentially Affected"
    NOT_AFFECTED = "Not Affected"
    REFERENCE = "Reference"


class SoftwareChange(BaseModel):
    change_id: str = Field(..., description="Unique change ID (e.g. CHG-001)")
    software_area: str = Field("General", description="Software area/module (e.g. Sketching, Assembly, Modeling)")
    feature_workflow: str = Field("", description="Feature or workflow specifically changed")
    previous_state: Optional[str] = Field(None, description="Previous state in older version")
    current_state: Optional[str] = Field(None, description="New/current state in updated software")
    change_type: ChangeType = Field(..., description="Standardized category of change")
    source_location: str = Field("Vendor Release Notes", description="Source location of change note")
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.HIGH, description="Confidence in change extraction")
    title: str = Field(..., description="Short title of the change")
    description: str = Field(..., description="Full description of the software change")
    affected_subsystem: str = Field("General", description="Module or subsystem (alias for software_area)")
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
    software_change: str = Field(default="", description="Actual change in the software itself (NOT course path!)")
    previous_state: Optional[str] = Field(None, description="What the old course currently represents")
    current_state: Optional[str] = Field(None, description="What the new/current software represents")
    document: str = Field(..., description="Exact filename")
    exact_location: str = Field(..., description="Exact location (Document → Module → Lesson → Page/Slide/Row/Section)")
    affected_content: str = Field(..., description="Quote or summary of the relevant existing content")
    evidence: str = Field(..., description="Exact source evidence used to identify dependency (verbatim quote)")
    why_flagged: str = Field(..., description="Why affected: explains relationship between software change and course")
    recommended_action: str = Field(..., description="Concrete author directive (e.g. Replace screenshot...)")
    priority: PriorityLevel
    confidence: ConfidenceLevel
    change_type: ChangeType
    impact_status: ImpactStatus = ImpactStatus.AFFECTED
    change_summary: str = ""
    old_state: Optional[str] = None
    new_state: Optional[str] = None
    requires_manual_review: bool = False
    chunk_id: str = ""

    def model_post_init(self, __context: Any) -> None:
        if not self.software_change and self.change_summary:
            self.software_change = self.change_summary
        elif not self.change_summary and self.software_change:
            self.change_summary = self.software_change

        if self.previous_state and not self.old_state:
            self.old_state = self.previous_state
        elif self.old_state and not self.previous_state:
            self.previous_state = self.old_state

        if self.current_state and not self.new_state:
            self.new_state = self.current_state
        elif self.new_state and not self.current_state:
            self.current_state = self.new_state


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
    finding_ref: Optional[str] = None


class DocumentSummary(BaseModel):
    document: str
    status: ImpactStatus
    highest_priority: Optional[PriorityLevel] = None
    affected_locations_count: int = 0
    change_types: List[ChangeType] = Field(default_factory=list)
    action_summary: str = "No action required"
    non_impact_reason: Optional[str] = None
    findings: List[Finding] = Field(default_factory=list)


class TraceabilityItem(BaseModel):
    trace_id: str
    change_id: str
    software_change: str
    source_evidence: str
    affected_content: str
    exact_location: str
    required_action: str
    priority: PriorityLevel
    document: str


class GapAnalysisReport(BaseModel):
    report_id: str
    software: str
    current_version: str
    new_version: str
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_documents: int = 0
    affected_documents_count: int = 0
    potentially_affected_count: int = 0
    high_priority_count: int = 0
    medium_priority_count: int = 0
    low_priority_count: int = 0
    changes: List[SoftwareChange] = Field(default_factory=list, description="Section 2: Software Change Inventory")
    document_summaries: List[DocumentSummary] = Field(default_factory=list, description="Section 3: Document Impact Map")
    action_plan: List[ActionItem] = Field(default_factory=list, description="Section 4: Author Action Plan")
    findings: List[Finding] = Field(default_factory=list, description="Section 5: Detailed Findings & Grounded Evidence")
    unaffected_documents: List[DocumentSummary] = Field(default_factory=list, description="Section 6: Verified Unaffected Course Material")
    reference_documents: List[DocumentSummary] = Field(default_factory=list, description="Section 7: Current-State Reference Documents")
    traceability_matrix: List[TraceabilityItem] = Field(default_factory=list, description="Section 8: Traceability Matrix")
