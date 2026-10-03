import os
import json
from typing import Dict, Any
from crewai.tools import tool
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

@tool("PDF Executive Summary Generator")
def create_pdf_report(
    output_filename: str,
    report_title: str,
    executive_summary_text: str,
    data_metrics_summary: str = "{}"
) -> str:
    """
    Generates a styled, publication-ready Executive PDF Report using ReportLab.
    
    Args:
        output_filename (str): Desired PDF path (e.g., 'reports/Executive_Summary.pdf').
        report_title (str): Title header for the executive report.
        executive_summary_text (str): Complete narrative findings from Reporting Agent.
        data_metrics_summary (str): JSON string containing summary data metrics.
        
    Returns:
        str: Confirmation message with generated PDF file location.
    """
    os.makedirs(os.path.dirname(output_filename) if os.path.dirname(output_filename) else ".", exist_ok=True)
    doc = SimpleDocTemplate(output_filename, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=12
    )

    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=14,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )

    story = []

    # Title Block
    story.append(Paragraph(report_title, title_style))
    story.append(Paragraph("AutoInsight AI - Autonomous Analytics Report", ParagraphStyle('Subtitle', fontName='Helvetica-Oblique', fontSize=10, textColor=colors.HexColor('#64748B'))))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2563EB'), spaceAfter=15))

    # Metric Table (if provided)
    try:
        metrics = json.loads(data_metrics_summary)
        if "overview" in metrics:
            story.append(Paragraph("Dataset Overview", h2_style))
            overview = metrics["overview"]
            table_data = [
                ["Total Rows", "Total Columns", "Duplicate Rows", "Numeric Columns"],
                [
                    str(overview.get("total_rows", 0)),
                    str(overview.get("total_columns", 0)),
                    str(overview.get("duplicate_rows", 0)),
                    str(overview.get("numeric_columns_count", 0))
                ]
            ]
            t = Table(table_data, colWidths=[130, 130, 130, 130])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(t)
            story.append(Spacer(1, 15))
    except Exception:
        pass

    # Executive Summary Paragraphs
    story.append(Paragraph("Executive Narrative & Strategic Insights", h2_style))
    
    # Process line breaks and clean text for ReportLab Paragraph compatibility
    paragraphs = executive_summary_text.split("\n\n")
    for para in paragraphs:
        if para.strip():
            clean_para = para.strip().replace("\n", "<br/>")
            if clean_para.startswith("#"):
                clean_para = clean_para.lstrip("#").strip()
                story.append(Paragraph(clean_para, h2_style))
            else:
                story.append(Paragraph(clean_para, body_style))

    doc.build(story)
    return f"PDF report successfully created at: {output_filename}"
