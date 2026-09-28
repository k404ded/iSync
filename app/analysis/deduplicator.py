"""
Deduplicator for iSync findings.
Enforces the unique Change -> Affected Document -> Exact Location -> Action relationship.
Eliminates redundant micro-alerts on the same page/slide.
"""

from typing import List
from app.models.schemas import Finding


class FindingDeduplicator:
    """Removes duplicate or redundant findings while preserving unique document-location impacts."""

    @staticmethod
    def deduplicate(findings: List[Finding]) -> List[Finding]:
        unique_findings: List[Finding] = []
        seen_keys = set()
        finding_num = 1

        for f in findings:
            # Aspect distinguishes screenshot replacement from text review
            aspect = "screenshot" if ("screenshot" in f.recommended_action.lower() or "figure" in f.evidence.lower()) else "text"
            
            # Deduplication key based on change, document, exact location, and aspect
            dedup_key = (f.change_id, f.document, f.exact_location, aspect)

            if dedup_key in seen_keys:
                continue

            # Update finding ID sequentially
            f_clean = f.model_copy(update={"finding_id": f"FND-{finding_num:03d}"})
            unique_findings.append(f_clean)
            seen_keys.add(dedup_key)
            finding_num += 1

        return unique_findings
