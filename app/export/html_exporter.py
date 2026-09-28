"""
HTML Report Exporter for iSync.
Produces a clean, standalone HTML gap analysis report with executive metrics,
Document Impact Map, Author Action Plan, and Detailed Findings.
"""

from app.models.schemas import GapAnalysisReport, PriorityLevel


class HTMLExporter:
    @staticmethod
    def export(report: GapAnalysisReport) -> str:
        # Document Impact Map table rows
        doc_rows_html = []
        for d in report.document_summaries:
            pri_badge = f"<span class='badge-{d.highest_priority.value.lower()}'>{d.highest_priority.value}</span>" if d.highest_priority else "—"
            status_cls = "status-affected" if d.status.value == "Affected" else "status-unaffected"
            types_str = ", ".join([t.value for t in d.change_types]) if d.change_types else "None"
            doc_rows_html.append(f"""
            <tr>
                <td><strong>{d.document}</strong></td>
                <td><span class='{status_cls}'>{d.status.value}</span></td>
                <td>{pri_badge}</td>
                <td>{d.affected_locations_count}</td>
                <td>{types_str}</td>
                <td>{d.action_summary}</td>
            </tr>
            """)

        # Action plan cards
        action_cards_html = []
        for idx, act in enumerate(report.action_plan, 1):
            pri_cls = f"priority-{act.priority.value.lower()}"
            transition_html = ""
            if act.old_state and act.new_state:
                transition_html = f"""
                <div class="transition-box">
                    <span class="old-state">OLD: {act.old_state}</span>
                    <span class="arrow">➔</span>
                    <span class="new-state">NEW: {act.new_state}</span>
                </div>
                """

            action_cards_html.append(f"""
            <div class="action-card {pri_cls}">
                <div class="action-header">
                    <span class="action-num">#{idx}</span>
                    <span class="action-type">{act.action_type}</span>
                    <span class="badge-{act.priority.value.lower()}">{act.priority.value}</span>
                    <span class="doc-label">{act.document}</span>
                </div>
                <div class="action-title">{act.change_title}</div>
                <div class="loc-label">📍 {act.exact_location}</div>
                {transition_html}
                <div class="action-desc">👉 {act.instructions}</div>
            </div>
            """)

        # Detailed findings
        findings_html = []
        for f in report.findings:
            pri_cls = f"priority-{f.priority.value.lower()}"
            findings_html.append(f"""
            <div class="finding-card {pri_cls}">
                <div class="finding-top">
                    <div>
                        <span class="finding-id">{f.finding_id}</span>
                        <span class="badge-{f.priority.value.lower()}">{f.priority.value} Priority</span>
                        <span class="conf-badge">Confidence: {f.confidence.value}</span>
                        <span class="type-badge">{f.change_type.value}</span>
                    </div>
                    <span class="doc-name">{f.document}</span>
                </div>
                <h3>{f.change_summary}</h3>
                <div class="loc-banner">📍 Exact Location: {f.exact_location}</div>
                
                <div class="section-block">
                    <div class="block-title">AFFECTED COURSE CONTENT</div>
                    <div class="content-box">{f.affected_content}</div>
                </div>

                <div class="section-block">
                    <div class="block-title">GROUNDED EVIDENCE</div>
                    <div class="evidence-box">"{f.evidence}"</div>
                </div>

                <div class="section-block">
                    <div class="block-title">WHY THIS WAS FLAGGED</div>
                    <div class="why-box">{f.why_flagged}</div>
                </div>

                <div class="section-block">
                    <div class="block-title">RECOMMENDED AUTHOR ACTION</div>
                    <div class="author-action-box">{f.recommended_action}</div>
                </div>
            </div>
            """)

        html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>iSync Gap Analysis Report - {report.software} ({report.current_version} → {report.new_version})</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f8fafc;
            color: #0f172a;
            margin: 0;
            padding: 32px;
            line-height: 1.5;
        }}
        .header {{
            background: #0f172a;
            color: #ffffff;
            padding: 24px 30px;
            border-radius: 10px;
            margin-bottom: 24px;
        }}
        .header h1 {{ margin: 0 0 6px 0; font-size: 24px; }}
        .header p {{ margin: 0; color: #94a3b8; font-size: 13px; }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 12px;
            margin-bottom: 28px;
        }}
        .metric-box {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 16px;
        }}
        .metric-val {{ font-size: 24px; font-weight: 700; color: #0f172a; }}
        .metric-lbl {{ font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 600; margin-top: 4px; }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #e2e8f0;
            margin-bottom: 30px;
        }}
        th, td {{
            padding: 12px 14px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
            font-size: 13px;
        }}
        th {{ background: #f1f5f9; font-weight: 600; color: #475569; }}
        
        .badge-high {{ background: #fee2e2; color: #b91c1c; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; }}
        .badge-medium {{ background: #fef3c7; color: #b45309; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; }}
        .badge-low {{ background: #dbeafe; color: #1d4ed8; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; }}
        .status-affected {{ color: #dc2626; font-weight: 700; }}
        .status-unaffected {{ color: #16a34a; font-weight: 600; }}

        .action-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #3b82f6;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 14px;
        }}
        .action-card.priority-high {{ border-left-color: #dc2626; }}
        .action-card.priority-medium {{ border-left-color: #d97706; }}
        .action-card.priority-low {{ border-left-color: #2563eb; }}
        
        .action-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }}
        .action-num {{ font-weight: 700; color: #475569; }}
        .action-type {{ font-weight: 600; color: #1e293b; font-size: 13px; }}
        .doc-label {{ margin-left: auto; font-size: 12px; color: #64748b; }}
        .action-title {{ font-size: 15px; font-weight: 600; margin-bottom: 4px; }}
        .loc-label {{ font-size: 12px; color: #475569; margin-bottom: 8px; font-family: monospace; }}
        
        .transition-box {{
            background: #f1f5f9;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 13px;
            margin: 8px 0;
            display: inline-block;
        }}
        .old-state {{ color: #b91c1c; text-decoration: line-through; }}
        .arrow {{ color: #64748b; margin: 0 8px; }}
        .new-state {{ color: #15803d; font-weight: 600; }}
        .action-desc {{ font-size: 13px; color: #1e40af; font-weight: 500; margin-top: 6px; }}

        .finding-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 16px;
        }}
        .finding-top {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
        .finding-id {{ font-weight: 700; margin-right: 6px; }}
        .conf-badge, .type-badge {{ background: #f1f5f9; color: #334155; padding: 2px 6px; border-radius: 4px; font-size: 11px; margin-left: 4px; }}
        .doc-name {{ font-size: 12px; color: #64748b; font-weight: 500; }}
        .loc-banner {{ background: #f8fafc; border-left: 3px solid #3b82f6; padding: 8px 12px; font-size: 12px; font-family: monospace; margin-bottom: 12px; }}
        .section-block {{ margin-bottom: 10px; }}
        .block-title {{ font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 4px; }}
        .content-box {{ background: #f8fafc; padding: 10px; border-radius: 6px; font-size: 13px; color: #1e293b; border: 1px solid #e2e8f0; }}
        .evidence-box {{ background: #fffbeb; padding: 10px; border-radius: 6px; font-size: 13px; color: #92400e; font-style: italic; border: 1px solid #fde68a; }}
        .why-box {{ font-size: 13px; color: #334155; }}
        .author-action-box {{ background: #eff6ff; padding: 10px; border-radius: 6px; font-size: 13px; color: #1e40af; font-weight: 600; border: 1px solid #bfdbfe; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>iSync — Intelligent Course Update Gap Analysis Report</h1>
        <p>iGETIT Content Architecture • Tata Technologies | Report ID: {report.report_id} | Analyzed: {report.analyzed_at.strftime('%Y-%m-%d %H:%M UTC')}</p>
    </div>

    <h2>1. Executive Summary</h2>
    <div class="metrics-grid">
        <div class="metric-box"><div class="metric-val">{report.software}</div><div class="metric-lbl">Software</div></div>
        <div class="metric-box"><div class="metric-val">{report.current_version} → {report.new_version}</div><div class="metric-lbl">Version Delta</div></div>
        <div class="metric-box"><div class="metric-val">{report.total_documents}</div><div class="metric-lbl">Documents Analyzed</div></div>
        <div class="metric-box"><div class="metric-val">{report.affected_documents_count}</div><div class="metric-lbl">Documents Affected</div></div>
        <div class="metric-box"><div class="metric-val" style="color: #dc2626;">{report.high_priority_count}</div><div class="metric-lbl">High Priority</div></div>
        <div class="metric-box"><div class="metric-val" style="color: #d97706;">{report.medium_priority_count}</div><div class="metric-lbl">Medium Priority</div></div>
        <div class="metric-box"><div class="metric-val" style="color: #2563eb;">{report.low_priority_count}</div><div class="metric-lbl">Low Priority</div></div>
    </div>

    <h2>2. Document Impact Map</h2>
    <table>
        <thead>
            <tr>
                <th>Document</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Affected Locations</th>
                <th>Change Types</th>
                <th>Required Action</th>
            </tr>
        </thead>
        <tbody>
            {"".join(doc_rows_html)}
        </tbody>
    </table>

    <h2>3. Author Action Plan</h2>
    {"".join(action_cards_html)}

    <h2>4. Detailed Findings Dossier</h2>
    {"".join(findings_html)}
</body>
</html>
"""
        return html_out
