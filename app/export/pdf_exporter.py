"""
PDF Report Exporter for iSync using ReportLab.
Renders an executive dossier with Document Impact Map, Action Plan, and Findings.
"""

import io
from app.models.schemas import GapAnalysisReport, PriorityLevel
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    HAS_REPORTLAB = True
except (ImportError, Exception):
    HAS_REPORTLAB = False


class PDFExporter:
    @staticmethod
    def export(report: GapAnalysisReport) -> bytes:
        if not HAS_REPORTLAB:
            raise RuntimeError("ReportLab library is not available in this environment for PDF export.")
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#0f172a"),
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#64748b"),
        )
        section_style = ParagraphStyle(
            "DocSection",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
        )
        cell_bold = ParagraphStyle(
            "CellBold",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#0f172a"),
        )
        cell_text = ParagraphStyle(
            "CellText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#334155"),
        )

        story = []

        # Title
        story.append(Paragraph("iSync — Intelligent Course Update Gap Analysis Report", title_style))
        story.append(
            Paragraph(
                f"iGETIT • Tata Technologies | Software: {report.software} ({report.current_version} → {report.new_version}) | "
                f"Report: {report.report_id}",
                subtitle_style,
            )
        )
        story.append(Spacer(1, 12))

        # Metrics
        m_data = [
            [
                Paragraph("<b>Metric</b>", cell_bold),
                Paragraph("<b>Value</b>", cell_bold),
                Paragraph("<b>Priority Level</b>", cell_bold),
                Paragraph("<b>Count</b>", cell_bold),
            ],
            [
                Paragraph("Documents Analyzed", cell_text),
                Paragraph(str(report.total_documents), cell_bold),
                Paragraph("High Priority", cell_text),
                Paragraph(f"<font color='#dc2626'><b>{report.high_priority_count}</b></font>", cell_bold),
            ],
            [
                Paragraph("Documents Affected", cell_text),
                Paragraph(str(report.affected_documents_count), cell_bold),
                Paragraph("Medium Priority", cell_text),
                Paragraph(f"<font color='#d97706'><b>{report.medium_priority_count}</b></font>", cell_bold),
            ],
            [
                Paragraph("Total Findings", cell_text),
                Paragraph(str(len(report.findings)), cell_bold),
                Paragraph("Low Priority", cell_text),
                Paragraph(f"<font color='#2563eb'><b>{report.low_priority_count}</b></font>", cell_bold),
            ],
        ]
        t_m = Table(m_data, colWidths=[140, 110, 150, 140])
        t_m.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(t_m)
        story.append(Spacer(1, 14))

        # Document Impact Map
        story.append(Paragraph("Document Impact Map", section_style))
        story.append(Spacer(1, 6))

        dim_data = [
            [
                Paragraph("<b>Document</b>", cell_bold),
                Paragraph("<b>Status</b>", cell_bold),
                Paragraph("<b>Priority</b>", cell_bold),
                Paragraph("<b>Locations</b>", cell_bold),
                Paragraph("<b>Action Summary</b>", cell_bold),
            ]
        ]
        for d in report.document_summaries:
            p_val = d.highest_priority.value if d.highest_priority else "—"
            dim_data.append([
                Paragraph(d.document, cell_bold),
                Paragraph(d.status.value, cell_text),
                Paragraph(p_val, cell_text),
                Paragraph(str(d.affected_locations_count), cell_text),
                Paragraph(d.action_summary[:120], cell_text),
            ])

        t_dim = Table(dim_data, colWidths=[140, 70, 60, 60, 210])
        t_dim.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(t_dim)
        story.append(Spacer(1, 14))

        # Author Action Plan
        story.append(Paragraph("Author Action Plan", section_style))
        story.append(Spacer(1, 6))

        for idx, act in enumerate(report.action_plan, 1):
            act_rows = [
                [
                    Paragraph(f"<b>#{idx} {act.action_type}</b> ({act.priority.value} Priority)", cell_bold),
                    Paragraph(f"<b>Doc:</b> {act.document}", cell_text),
                ],
                [
                    Paragraph("<b>Location:</b>", cell_bold),
                    Paragraph(act.exact_location, cell_text),
                ],
                [
                    Paragraph("<b>Required Action:</b>", cell_bold),
                    Paragraph(f"<b>{act.instructions}</b>", cell_text),
                ],
            ]
            if act.old_state and act.new_state:
                act_rows.append([
                    Paragraph("<b>Transition:</b>", cell_bold),
                    Paragraph(f"FROM: {act.old_state} ➔ TO: {act.new_state}", cell_text),
                ])

            t_act = Table(act_rows, colWidths=[110, 430])
            t_act.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eff6ff")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bfdbfe")),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ])
            )
            story.append(t_act)
            story.append(Spacer(1, 6))

        doc.build(story)
        return buf.getvalue()
