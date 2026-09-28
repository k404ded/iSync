"""
Change Extractor and Normalizer for iSync.
Transforms unstructured change text, release notes, or vendor deltas into structured SoftwareChange objects.
"""

import re
from typing import List, Optional
from app.models.schemas import SoftwareChange, ChangeType


class ChangeExtractor:
    """Extracts and normalizes software changes into typed SoftwareChange objects."""

    def extract_changes(
        self,
        raw_text: str,
        software_name: str,
        current_version: str,
        new_version: str,
    ) -> List[SoftwareChange]:
        if not raw_text or not raw_text.strip():
            return []

        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        # Filter out generic header/preamble lines before the first numbered or bulleted change
        filtered_lines: List[str] = []
        has_started_changes = False
        change_header_regex = re.compile(
            r"^(?:CHANGE\s+\d+:?|[-*•]\s+|\d+[\.\)]\s+|FEATURE\s+\d+:?|UPDATE\s+\d+:?)",
            re.IGNORECASE,
        )

        for line in lines:
            if change_header_regex.match(line):
                has_started_changes = True
            elif not has_started_changes:
                # Skip document titles like "SOLIDWORKS 2025 Release Notes & Software Delta:"
                if any(w in line.lower() for w in ["release notes", "delta", "summary", "version", "what's new"]) or line.endswith(":"):
                    continue
            filtered_lines.append(line)

        # Segment into discrete change blocks
        blocks: List[str] = []
        current_block: List[str] = []

        for line in filtered_lines:
            if change_header_regex.match(line):
                if current_block:
                    blocks.append(" ".join(current_block))
                    current_block = []
                cleaned = change_header_regex.sub("", line).strip()
                if cleaned:
                    current_block.append(cleaned)
            else:
                if current_block:
                    current_block.append(line)
                elif has_started_changes:
                    current_block.append(line)

        if current_block:
            blocks.append(" ".join(current_block))

        # Fallback if no bullet points or CHANGE headers were detected
        if not blocks:
            # Split by double newline or paragraph
            paras = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
            blocks = paras if paras else [raw_text.strip()]

        changes: List[SoftwareChange] = []
        change_counter = 1

        for block in blocks:
            clean_b = " ".join(block.split())
            if not clean_b or len(clean_b) < 10:
                continue

            lower_b = clean_b.lower()

            # Classify ChangeType
            change_type = ChangeType.FEATURE_CHANGE
            if any(k in lower_b for k in ["deprecated", "obsolete", "discontinued"]):
                change_type = ChangeType.DEPRECATED_FEATURE
            elif any(k in lower_b for k in ["removed", "deleted", "eliminated"]):
                change_type = ChangeType.REMOVED_FEATURE
            elif any(k in lower_b for k in ["rename", "renamed to", "rebranded", "is now called"]):
                change_type = ChangeType.TERMINOLOGY_CHANGE
            elif any(k in lower_b for k in ["toolbar", "ui ", "interface", "dialog", "icon", "redesign", "palette", "ribbon", "menu"]):
                change_type = ChangeType.UI_CHANGE
            elif any(k in lower_b for k in ["moved", "workflow", "process", "steps", "reordered", "docked", "dialog to"]):
                change_type = ChangeType.WORKFLOW_CHANGE
            elif any(k in lower_b for k in ["brand new", "introduced", "added", "new functionality", "new feature"]):
                change_type = ChangeType.NEW_FEATURE
            elif any(k in lower_b for k in ["performance", "speed", "memory", "threading", "compute"]):
                change_type = ChangeType.PERFORMANCE_TECHNICAL
            elif any(k in lower_b for k in ["behavior", "modified", "calculation", "algorithm"]):
                change_type = ChangeType.MODIFIED_BEHAVIOR

            # Extract old and new terminology
            old_term, new_term = None, None
            rename_match = re.search(
                r"['\"]?([A-Za-z0-9\s_-]+?)['\"]?\s+(?:has been renamed to|renamed to|is now|rebranded as)\s+['\"]?([A-Za-z0-9\s_-]+?)['\"]?(?:[\.\,\;]|\s+(?:to reflect|in favor of|for|\.|$))",
                clean_b,
                re.IGNORECASE,
            )
            if rename_match:
                old_term = rename_match.group(1).strip()
                new_term = rename_match.group(2).strip()

            # Extract workflow transitions if present
            old_wf, new_wf = None, None
            moved_match = re.search(
                r"(\w+[\s\w]*panel|\w+[\s\w]*toolbar|\w+[\s\w]*window)\s+moved\s+from\s+(?:the\s+)?([^\.]+?)\s+(?:directly\s+)?into\s+(?:the\s+)?([^\.]+)",
                clean_b,
                re.IGNORECASE,
            )
            if moved_match:
                subject = moved_match.group(1).strip()
                old_wf = f"{subject} in {moved_match.group(2).strip()}"
                new_wf = f"{subject} in {moved_match.group(3).strip()}"

            # Determine affected subsystem
            subsystem = "General Modeling"
            if any(k in lower_b for k in ["sketch", "sketching", "line", "spline", "circle", "rectangle"]):
                subsystem = "Sketching"
            elif any(k in lower_b for k in ["constraint", "mate", "assembly", "kinematic", "joint"]):
                subsystem = "Constraints & Assembly"
            elif any(k in lower_b for k in ["drawing", "drafting", "2d", "sheet", "annotation", "mbd"]):
                subsystem = "Drafting & Drawings"
            elif any(k in lower_b for k in ["hole", "wizard", "fastener", "boss", "extrude", "revolve"]):
                subsystem = "Part Features & Fasteners"
            elif any(k in lower_b for k in ["simulation", "motion", "stress", "fea", "flow"]):
                subsystem = "Simulation"

            # Extract keywords and stems
            raw_words = re.findall(r"\b[A-Za-z]{3,}\b", clean_b)
            stop_words = {
                "the", "and", "for", "with", "this", "that", "from", "has", "been",
                "was", "are", "into", "modernized", "solidworks", "updated", "feature",
            }
            keywords = []
            for w in raw_words:
                w_cap = w.capitalize()
                if w.lower() not in stop_words and w_cap not in keywords:
                    keywords.append(w_cap)

            if old_term and old_term not in keywords:
                keywords.insert(0, old_term)
            if new_term and new_term not in keywords:
                keywords.insert(1, new_term)

            # Title
            title = clean_b.split(".")[0].strip()
            if len(title) > 75:
                title = title[:72] + "..."

            change = SoftwareChange(
                change_id=f"CHG-{change_counter:03d}",
                title=title,
                change_type=change_type,
                description=clean_b,
                affected_subsystem=subsystem,
                old_term=old_term,
                new_term=new_term,
                old_workflow=old_wf,
                new_workflow=new_wf,
                keywords=keywords[:12],
            )
            changes.append(change)
            change_counter += 1

        return changes
