from __future__ import annotations

from io import BytesIO
from typing import Any, Dict

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


class ReportService:
    @staticmethod
    def create_incident_pdf(result: Dict[str, Any]) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=LETTER)
        styles = getSampleStyleSheet()
        story = []

        rca = result.get("rca", {})
        evidence = result.get("evidence", {})

        story.append(Paragraph("Production Incident Report", styles["Title"]))
        story.append(Spacer(1, 18))
        story.append(Paragraph(f"Incident ID: {result.get('incident_id', 'N/A')}", styles["Heading2"]))
        story.append(Paragraph(f"Order ID: {result.get('order_id', 'N/A')}", styles["BodyText"]))
        story.append(Paragraph(f"Root cause: {rca.get('root_cause', 'Unknown')}", styles["BodyText"]))
        story.append(Paragraph(f"Severity: {rca.get('severity', 'UNKNOWN')}", styles["BodyText"]))
        story.append(Paragraph(f"Confidence: {rca.get('confidence', 'UNKNOWN')}", styles["BodyText"]))
        story.append(Paragraph(f"Recommended action: {rca.get('recommended_action', 'Not specified')}", styles["BodyText"]))

        story.append(Spacer(1, 10))
        story.append(Paragraph("Evidence Summary", styles["Heading2"]))
        for section_name, rows in evidence.items():
            if rows:
                first_row = rows[0]
                summary = ", ".join(f"{key}: {value}" for key, value in first_row.items())
                story.append(Paragraph(f"{section_name.title()}: {summary}", styles["BodyText"]))

        doc.build(story)
        return buffer.getvalue()
