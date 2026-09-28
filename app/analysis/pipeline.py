"""
Pipeline Orchestrator for iSync.
Connects Change Extraction -> Ingestion -> Semantic Retrieval -> Impact Analysis -> Deduplication -> Action Plan.
Constructs the complete GapAnalysisReport with Document Summaries and Unaffected Document explanations.
"""

import uuid
from typing import List, Callable, Optional, Dict, Tuple
from datetime import datetime, timezone
from app.models.schemas import (
    SoftwareChange,
    ContentChunk,
    Finding,
    ActionItem,
    DocumentSummary,
    TraceabilityItem,
    GapAnalysisReport,
    ImpactStatus,
    PriorityLevel,
    ChangeType,
)
from app.analysis.change_extractor import ChangeExtractor
from app.analysis.semantic_retriever import SemanticRetriever
from app.analysis.impact_analyzer import ImpactAnalyzer
from app.analysis.deduplicator import FindingDeduplicator
from app.analysis.gemini_reasoner import GeminiReasoner


class GapAnalysisPipeline:
    def __init__(self):
        self.extractor = ChangeExtractor()
        self.retriever = SemanticRetriever()
        self.analyzer = ImpactAnalyzer()
        self.deduplicator = FindingDeduplicator()
        self.reasoner = GeminiReasoner()

    def run(
        self,
        software: str,
        current_version: str,
        new_version: str,
        change_text: str,
        all_chunks: List[ContentChunk],
        all_document_names: List[str],
        reference_document_names: Optional[List[str]] = None,
        progress_cb: Optional[Callable[[int, str], None]] = None,
    ) -> GapAnalysisReport:
        def notify(step: int, msg: str):
            if progress_cb:
                progress_cb(step, msg)

        # Step 1: Change Extraction
        notify(1, f"Extracting software changes for {software} ({current_version} → {new_version})...")
        changes = self.extractor.extract_changes(
            raw_text=change_text,
            software_name=software,
            current_version=current_version,
            new_version=new_version,
        )

        # Step 2: Content Cataloging
        notify(2, f"Indexed {len(all_chunks)} content chunks across {len(all_document_names)} course documents...")

        # Step 3: Hybrid Retrieval & Impact Analysis
        notify(3, "Mapping software changes against course curriculum using hybrid semantic reasoning...")
        raw_findings: List[Finding] = []
        finding_id_seq = 1

        for change in changes:
            candidates = self.retriever.retrieve_candidates(change, all_chunks)
            for cand in candidates:
                finding = self.analyzer.evaluate_candidate(cand, f"FND-{finding_id_seq:03d}")
                if finding:
                    raw_findings.append(finding)
                    finding_id_seq += 1

        # Step 4: Deduplication
        notify(4, "Deduplicating findings to enforce Change → Document → Location clarity...")
        findings = self.deduplicator.deduplicate(raw_findings)

        if self.reasoner.is_available and findings:
            notify(4, "Enriching findings via Gemini AI semantic reasoning...")
            chunk_map = {c.chunk_id: c for c in all_chunks}
            change_map = {c.change_id: c for c in changes}
            refined_findings = []
            for f in findings:
                c = chunk_map.get(f.chunk_id)
                chg = change_map.get(f.change_id)
                if c and chg:
                    refined_findings.append(self.reasoner.refine_finding(chg, c, f))
                else:
                    refined_findings.append(f)
            findings = refined_findings

        # Step 5: Document Summaries, Author Action Plan & Traceability Matrix
        notify(5, "Generating Document Impact Map, Action Plan, and Traceability Matrix...")
        doc_summaries, unaffected_docs, reference_docs = self._build_document_summaries(
            all_document_names, findings, changes, reference_document_names
        )
        action_plan = self._build_action_plan(findings)
        traceability_matrix = self._build_traceability_matrix(findings)

        # Metrics
        affected_count = len([d for d in doc_summaries if d.status == ImpactStatus.AFFECTED])
        pot_affected_count = len([d for d in doc_summaries if d.status == ImpactStatus.POTENTIALLY_AFFECTED])
        high_cnt = sum(1 for f in findings if f.priority == PriorityLevel.HIGH)
        med_cnt = sum(1 for f in findings if f.priority == PriorityLevel.MEDIUM)
        low_cnt = sum(1 for f in findings if f.priority == PriorityLevel.LOW)

        report = GapAnalysisReport(
            report_id=f"RPT-{uuid.uuid4().hex[:8].upper()}",
            software=software,
            current_version=current_version,
            new_version=new_version,
            analyzed_at=datetime.now(timezone.utc),
            total_documents=len(all_document_names),
            affected_documents_count=affected_count,
            potentially_affected_count=pot_affected_count,
            high_priority_count=high_cnt,
            medium_priority_count=med_cnt,
            low_priority_count=low_cnt,
            changes=changes,
            document_summaries=doc_summaries,
            findings=findings,
            action_plan=action_plan,
            unaffected_documents=unaffected_docs,
            reference_documents=reference_docs,
            traceability_matrix=traceability_matrix,
        )
        return report

    def _build_document_summaries(
        self,
        all_docs: List[str],
        findings: List[Finding],
        changes: List[SoftwareChange],
        reference_doc_names: Optional[List[str]] = None,
    ) -> Tuple[List[DocumentSummary], List[DocumentSummary], List[DocumentSummary]]:
        doc_findings_map: Dict[str, List[Finding]] = {d: [] for d in all_docs}
        for f in findings:
            if f.document in doc_findings_map:
                doc_findings_map[f.document].append(f)
            else:
                doc_findings_map[f.document] = [f]

        all_summaries: List[DocumentSummary] = []
        unaffected: List[DocumentSummary] = []
        reference_docs: List[DocumentSummary] = []

        ref_names_set = set(reference_doc_names or [])

        for doc_name, doc_fnds in doc_findings_map.items():
            # Check if this document is a current-state reference document
            is_ref = doc_name in ref_names_set or any(
                k in doc_name.lower()
                for k in ["release_notes", "release notes", "what's new", "whats_new", "whats new", "delta_doc", "reference"]
            )

            if is_ref:
                summary = DocumentSummary(
                    document=doc_name,
                    status=ImpactStatus.REFERENCE,
                    highest_priority=None,
                    affected_locations_count=0,
                    change_types=[],
                    action_summary="Current-state reference used to establish the target software state.",
                    non_impact_reason="Current-state reference used to establish the target software state.",
                    findings=[],
                )
                all_summaries.append(summary)
                reference_docs.append(summary)
            elif doc_fnds:
                # Prioritize: High > Medium > Low
                priorities = [f.priority for f in doc_fnds]
                highest_pri = PriorityLevel.HIGH if PriorityLevel.HIGH in priorities else (
                    PriorityLevel.MEDIUM if PriorityLevel.MEDIUM in priorities else PriorityLevel.LOW
                )
                types = list(dict.fromkeys([f.change_type for f in doc_fnds]))
                actions = "; ".join(list(dict.fromkeys([f.recommended_action.split(".")[0] for f in doc_fnds])))[:140]

                # Distinguish Affected vs Potentially Affected
                all_pot = all(f.impact_status == ImpactStatus.POTENTIALLY_AFFECTED for f in doc_fnds)
                status = ImpactStatus.POTENTIALLY_AFFECTED if all_pot else ImpactStatus.AFFECTED

                summary = DocumentSummary(
                    document=doc_name,
                    status=status,
                    highest_priority=highest_pri,
                    affected_locations_count=len(doc_fnds),
                    change_types=types,
                    action_summary=actions,
                    findings=doc_fnds,
                )
                all_summaries.append(summary)
            else:
                # Document was verified as NOT affected
                change_topics = ", ".join(list(dict.fromkeys([c.affected_subsystem for c in changes[:3]])))
                reason = f"Document inspected thoroughly; no dependencies or references found relating to changed software capabilities ({change_topics})."
                summary = DocumentSummary(
                    document=doc_name,
                    status=ImpactStatus.NOT_AFFECTED,
                    highest_priority=None,
                    affected_locations_count=0,
                    change_types=[],
                    action_summary="No changes required.",
                    non_impact_reason=reason,
                    findings=[],
                )
                all_summaries.append(summary)
                unaffected.append(summary)

        return all_summaries, unaffected, reference_docs

    def _build_traceability_matrix(self, findings: List[Finding]) -> List[TraceabilityItem]:
        matrix: List[TraceabilityItem] = []
        for idx, f in enumerate(findings, 1):
            matrix.append(
                TraceabilityItem(
                    trace_id=f"TRC-{idx:03d}",
                    change_id=f.change_id,
                    software_change=f.software_change or f.change_summary,
                    source_evidence=f.evidence,
                    affected_content=f.affected_content,
                    exact_location=f.exact_location,
                    required_action=f.recommended_action,
                    priority=f.priority,
                    document=f.document,
                )
            )
        return matrix

    def _build_action_plan(self, findings: List[Finding]) -> List[ActionItem]:
        plan: List[ActionItem] = []
        for idx, f in enumerate(findings, 1):
            action_type = "Update Content"
            if "screenshot" in f.recommended_action.lower() or "figure" in f.recommended_action.lower():
                action_type = "Replace Screenshot"
            elif f.change_type == ChangeType.TERMINOLOGY_CHANGE or f.old_state:
                action_type = "Replace Terminology"
            elif f.change_type in (ChangeType.DEPRECATED_FEATURE, ChangeType.REMOVED_FEATURE):
                action_type = "Remove Deprecated Workflow"
            elif f.change_type == ChangeType.WORKFLOW_CHANGE:
                action_type = "Update Procedural Steps"
            elif f.change_type == ChangeType.NEW_FEATURE:
                action_type = "Add Enhancement Exercise"

            item = ActionItem(
                action_id=f"ACT-{idx:03d}",
                document=f.document,
                change_title=f.change_summary,
                action_type=action_type,
                exact_location=f.exact_location,
                old_state=f.old_state,
                new_state=f.new_state,
                instructions=f.recommended_action,
                priority=f.priority,
            )
            plan.append(item)
        return plan
