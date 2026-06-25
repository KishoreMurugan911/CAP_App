"""PDF and Excel report generation."""

import io
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from utils.audit_findings import AuditFinding, findings_to_dataframe
from utils.config import LOGO_PATH


def generate_excel_report(
    df: pd.DataFrame,
    kpis: dict,
    findings: list[AuditFinding],
) -> bytes:
    """Generate multi-sheet Excel executive report."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        workbook = writer.book

        # Formats
        header_fmt = workbook.add_format({
            "bold": True, "bg_color": "#0F172A", "font_color": "#F8FAFC",
            "border": 1, "align": "center",
        })
        kpi_fmt = workbook.add_format({"bold": True, "font_size": 14, "font_color": "#3B82F6"})
        title_fmt = workbook.add_format({"bold": True, "font_size": 16, "font_color": "#0F172A"})

        # Executive Summary
        summary = pd.DataFrame([
            {"Metric": "Total Contracts", "Value": kpis.get("total", 0)},
            {"Metric": "Active Contracts", "Value": kpis.get("active", 0)},
            {"Metric": "Expiring within 30 Days", "Value": kpis.get("expiring_30", 0)},
            {"Metric": "Expiring within 90 Days", "Value": kpis.get("expiring_90", 0)},
            {"Metric": "Auto-Renew Contracts", "Value": kpis.get("auto_renew", 0)},
            {"Metric": "High-Risk Contracts", "Value": kpis.get("high_risk", 0)},
            {"Metric": "SLA Breaches", "Value": kpis.get("sla_breaches", 0)},
            {"Metric": "Contract Overruns", "Value": kpis.get("overruns", 0)},
            {"Metric": "Missing Approvals", "Value": kpis.get("missing_approvals", 0)},
        ])
        summary.to_excel(writer, sheet_name="Executive Summary", index=False, startrow=3)

        ws = writer.sheets["Executive Summary"]
        ws.write(0, 0, "CAP AI — Contract & Agreement Review Report", title_fmt)
        ws.write(1, 0, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        # Contracts
        if not df.empty:
            export_cols = [c for c in df.columns if not c.startswith("_")]
            df[export_cols].to_excel(writer, sheet_name="Contracts", index=False)

        # Findings
        findings_df = findings_to_dataframe(findings)
        findings_df.to_excel(writer, sheet_name="Audit Findings", index=False)

        # PowerPoint-ready tables
        if not df.empty and "Risk Category" in df.columns:
            risk_summary = df.groupby("Risk Category").size().reset_index(name="Count")
            risk_summary.to_excel(writer, sheet_name="PPT - Risk Summary", index=False)

        if not df.empty and "Vendor" in df.columns:
            vendor_spend = df.groupby("Vendor")["Contract Value"].sum().reset_index()
            vendor_spend.to_excel(writer, sheet_name="PPT - Vendor Spend", index=False)

    output.seek(0)
    return output.getvalue()


def generate_pdf_report(
    df: pd.DataFrame,
    kpis: dict,
    findings: list[AuditFinding],
    chart_figures: Optional[list[go.Figure]] = None,
) -> bytes:
    """Generate branded PDF executive report."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Title"], fontSize=18, textColor=colors.HexColor("#0F172A"))
    heading_style = ParagraphStyle("Heading", parent=styles["Heading2"], fontSize=14, textColor=colors.HexColor("#3B82F6"))
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, leading=14)

    elements = []

    if LOGO_PATH.exists():
        try:
            logo = Image(str(LOGO_PATH), width=1.5 * inch, height=1.5 * inch)
            elements.append(logo)
        except Exception:
            pass

    elements.append(Paragraph("Contract & Agreement Review Dashboard", title_style))
    elements.append(Paragraph(f"Executive Report — {datetime.now().strftime('%B %d, %Y')}", body_style))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("KPI Overview", heading_style))
    kpi_data = [[k.replace("_", " ").title(), str(v)] for k, v in kpis.items()]
    kpi_table = Table([["Metric", "Value"]] + kpi_data, colWidths=[3.5 * inch, 2 * inch])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Audit Findings & Recommendations", heading_style))
    if findings:
        for f in findings[:15]:
            elements.append(Paragraph(f"<b>{f.category}</b> — {f.finding}", body_style))
            elements.append(Paragraph(f"<i>Risk:</i> {f.risk}", body_style))
            elements.append(Paragraph(f"<i>Recommendation:</i> {f.recommendation}", body_style))
            elements.append(Spacer(1, 0.1 * inch))
    else:
        elements.append(Paragraph("No findings identified.", body_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
