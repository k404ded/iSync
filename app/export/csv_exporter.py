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
                "Document": f.document,
                "Priority": f.priority.value,
                "Confidence": f.confidence.value,
                "Change Type": f.change_type.value,
                "Location": f.exact_location,
                "Change": f.change_summary,
                "Affected Content": f.affected_content,
                "Evidence": f.evidence,
                "Why Flagged": f.why_flagged,
                "Recommended Action": f.recommended_action,
                "Old State": f.old_state or "",
                "New State": f.new_state or "",
            })

        df = pd.DataFrame(rows)
        buf = io.StringIO()
        df.to_csv(buf, index=False, encoding="utf-8")
        return buf.getvalue().encode("utf-8")
