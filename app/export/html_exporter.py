"""
HTML Report Exporter for iSync.
Produces a clean, standalone HTML gap analysis report with all 8 enterprise sections:
1. Executive Summary
2. Software Change Inventory
3. Document Impact Map
4. Author Action Plan
5. Detailed Findings & Grounded Evidence
6. Verified Unaffected Course Material
7. Current-State Reference Documents
8. Traceability Matrix
"""

from app.models.schemas import GapAnalysisReport, PriorityLevel, ImpactStatus


class HTMLExporter:
    @staticmethod
    def export(report: GapAnalysisReport) -> str:
        # Section 2: Change Inventory rows
        change_rows_html = []
        for c in report.changes:
            change_rows_html.append(f"""
            <tr>
                <td><strong>{c.change_id}</strong></td>
                <td>{c.software_area}</td>
                <td><strong>{c.title}</strong></td>
                <td>{c.change_type.value}</td>
                <td><code>{c.previous_state or '—'}</code></td>
                <td><code>{c.current_state or '—'}</code></td>
                <td>{c.confidence.value}</td>
            </tr>
            """)

        # Section 3: Document Impact Map table rows
        doc_rows_html = []
        for d in report.document_summaries:
            pri_badge = f"<span class='badge-{d.highest_priority.value.lower()}'>{d.highest_priority.value}</span>" if d.highest_priority else "—"
            if d.status == ImpactStatus.AFFECTED:
                status_html = "<span class='status-affected'>🔴 Affected</span>"
            elif d.status == ImpactStatus.POTENTIALLY_AFFECTED:
                status_html = "<span class='status-potential'>🟡 Potentially Affected</span>"
            elif d.status == ImpactStatus.REFERENCE:
                status_html = "<span class='status-reference'>🔵 Reference</span>"
            else:
                status_html = "<span class='status-unaffected'>🟢 Not Affected</span>"

            types_str = ", ".join([t.value for t in d.change_types]) if d.change_types else "None"
            doc_rows_html.append(f"""
            <tr>
                <td><strong>{d.document}</strong></td>
                <td>{status_html}</td>
                <td>{pri_badge}</td>
                <td>{d.affected_locations_count}</td>
                <td>{types_str}</td>
                <td>{d.action_summary}</td>
            </tr>
            """)

        # Section 4: Action plan cards
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

        # Section 5: Detailed findings
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
                <h3>{f.software_change or f.change_summary}</h3>
                <div class="loc-banner">📍 Exact Location: {f.exact_location}</div>
                
                <div class="section-block">
                    <div class="block-title">EXISTING COURSE CONTENT</div>
                    <div class="content-box">{f.affected_content}</div>
                </div>

                <div class="section-block">
                    <div class="block-title">GROUNDED EVIDENCE (Verbatim Source Quote)</div>
                    <div class="evidence-box">"{f.evidence}"</div>
                </div>

                <div class="section-block">
                    <div class="block-title">WHY THIS IS AFFECTED</div>
                    <div class="why-box">{f.why_flagged}</div>
                </div>

                <div class="section-block">
                    <div class="block-title">REQUIRED AUTHOR ACTION</div>
                    <div class="author-action-box">👉 {f.recommended_action}</div>
                </div>
            </div>
            """)

        # Section 6: Verified Unaffected Material
        unaffected_html = []
        if report.unaffected_documents:
            for u in report.unaffected_documents:
                unaffected_html.append(f"""
                <div class="unaffected-card">
                    <h4>🟢 {u.document} — Confirmed Unaffected</h4>
                    <p><strong>Verification Reason:</strong> {u.non_impact_reason or 'No conflicting dependencies found.'}</p>
                    <p><strong>Author Directive:</strong> <code>No changes required.</code></p>
                </div>
                """)
        else:
            unaffected_html.append("<p>All analyzed documents had at least one impacted area.</p>")

        # Section 7: Reference Documents
        reference_html = []
        if report.reference_documents:
            for r in report.reference_documents:
                reference_html.append(f"""
                <div class="reference-card">
                    <h4>🔵 {r.document} — Current-State Reference</h4>
                    <p><strong>Role:</strong> Current-state reference used to establish the target software state.</p>
                </div>
                """)
        else:
            reference_html.append("<p>Analysis performed using parsed vendor release change notes.</p>")

        # Section 8: Traceability Matrix rows
        trace_rows_html = []
        for t in report.traceability_matrix:
            trace_rows_html.append(f"""
            <tr>
                <td><strong>{t.trace_id}</strong></td>
                <td>{t.software_change}</td>
                <td><strong>{t.document}</strong></td>
                <td><code>{t.exact_location}</code></td>
                <td><em>"{t.source_evidence}"</em></td>
                <td>{t.required_action}</td>
                <td><span class='badge-{t.priority.value.lower()}'>{t.priority.value}</span></td>
            </tr>
            """)

        html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>iSync Gap Analysis Report — {report.software} ({report.current_version} → {report.new_version})</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.5;
            color: #1e293b;
            background: #f8fafc;
            padding: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: #ffffff;
            padding: 24px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            margin-bottom: 24px;
        }}
        h1 {{ margin: 0 0 6px 0; font-size: 24px; color: #0f172a; }}
        h2 {{ font-size: 18px; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 32px; }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 12px;
            margin: 20px 0;
        }}
        .metric-box {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 12px;
            text-align: center;
        }}
        .metric-val {{ font-size: 20px; font-weight: 700; color: #0f172a; }}
        .metric-lbl {{ font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 600; margin-top: 4px; }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #e2e8f0;
            margin: 16px 0;
        }}
        th, td {{
            padding: 10px 14px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
            font-size: 13px;
        }}
        th {{ background: #f1f5f9; font-weight: 600; color: #475569; }}
        
        .badge-high {{ background: #fee2e2; color: #b91c1c; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; }}
        .badge-medium {{ background: #fef3c7; color: #b45309; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; }}
        .badge-low {{ background: #dbeafe; color: #1d4ed8; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; }}
        .status-affected {{ color: #dc2626; font-weight: 700; }}
        .status-potential {{ color: #d97706; font-weight: 700; }}
        .status-reference {{ color: #2563eb; font-weight: 700; }}
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
        
        .unaffected-card, .reference-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 14px 18px;
            margin-bottom: 12px;
        }}
        .unaffected-card h4, .reference-card h4 {{ margin: 0 0 6px 0; font-size: 14px; color: #0f172a; }}
        .unaffected-card p, .reference-card p {{ margin: 3px 0; font-size: 13px; color: #475569; }}
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

    <h2>2. Software Change Inventory</h2>
    <table>
        <thead>
            <tr>
                <th>Change ID</th>
                <th>Software Area</th>
                <th>Feature / Workflow</th>
                <th>Change Type</th>
                <th>Previous State</th>
                <th>Current State</th>
                <th>Confidence</th>
            </tr>
        </thead>
        <tbody>
            {"".join(change_rows_html)}
        </tbody>
    </table>

    <h2>3. Document Impact Map</h2>
    <table>
        <thead>
            <tr>
                <th>Document</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Affected Locations</th>
                <th>Change Categories</th>
                <th>Required Action</th>
            </tr>
        </thead>
        <tbody>
            {"".join(doc_rows_html)}
        </tbody>
    </table>

    <h2>4. Author Action Plan</h2>
    {"".join(action_cards_html)}

    <h2>5. Detailed Findings & Grounded Evidence</h2>
    {"".join(findings_html)}

    <h2>6. Verified Unaffected Course Material</h2>
    {"".join(unaffected_html)}

    <h2>7. Current-State Reference Documents</h2>
    {"".join(reference_html)}

    <h2>8. Traceability Matrix</h2>
    <table>
        <thead>
            <tr>
                <th>Trace ID</th>
                <th>Software Change</th>
                <th>Document</th>
                <th>Exact Location</th>
                <th>Source Grounded Evidence</th>
                <th>Required Author Action</th>
                <th>Priority</th>
            </tr>
        </thead>
        <tbody>
            {"".join(trace_rows_html)}
        </tbody>
    </table>
</body>
</html>
"""
        return html_out
