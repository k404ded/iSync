"""
CSV Exporter for iSync Gap Analysis.
"""

import io
import pandas as pd
from app.models.schemas import GapAnalysisReport


class CSVExporter:
    @staticmethod
    def export(report: GapAnalysisReport) -> bytes:
        rows = []
        for f in report.findings:
            rows.append({
                "Finding ID": f.finding_id,
                "Change ID": f.change_id,
                "Software Change": f.software_change or f.change_summary,
                "Document": f.document,
                "Exact Location": f.exact_location,
                "Priority": f.priority.value,
                "Confidence": f.confidence.value,
                "Change Type": f.change_type.value,
                "Previous State": f.previous_state or f.old_state or "",
                "Current State": f.current_state or f.new_state or "",
                "Affected Content": f.affected_content,
                "Grounded Evidence": f.evidence,
                "Why Affected": f.why_flagged,
                "Required Author Action": f.recommended_action,
            })

        df = pd.DataFrame(rows)
        buf = io.StringIO()
        df.to_csv(buf, index=False, encoding="utf-8")
        return buf.getvalue().encode("utf-8")
