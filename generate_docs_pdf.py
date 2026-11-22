"""
Generate a professional PDF document for 'Documentation of the Approach Used to Build PartPulse'
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, 755, "PartPulse — Documentation of Technical Approach")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 747, 558, 747)
            
        # Footer (all pages)
        footer_text = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(558, 36, footer_text)
        self.drawString(54, 36, "Confidential & Proprietary — Engineering Project Submission")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        self.restoreState()


def build_pdf(filepath):
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    navy = colors.HexColor("#091726")
    teal = colors.HexColor("#0D9488")
    slate = colors.HexColor("#334155")
    muted = colors.HexColor("#64748B")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=navy,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=teal,
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=navy,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=teal,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=slate,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=slate,
        leftIndent=15,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        "Callout_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#0F172A")
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph("PartPulse: Quality Signal Radar", title_style))
    story.append(Paragraph("Documentation of Technical Approach & Implementation Architecture", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=teal, spaceBefore=0, spaceAfter=12))

    # Meta Table
    meta_data = [
        [Paragraph("<b>Project:</b> PartPulse Automotive Quality Intelligence", body_style),
         Paragraph("<b>Date:</b> November 2026", body_style)],
        [Paragraph("<b>Author / Candidate:</b> KRRISHNATH", body_style),
         Paragraph("<b>Repository:</b> github.com/KRRISHNATH/partpulse-quality-signals", body_style)],
        [Paragraph("<b>Production URL:</b> partpulse-quality-signals-*.streamlit.app", body_style),
         Paragraph("<b>Data Source:</b> U.S. Federal NHTSA Complaints API", body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[250, 254])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # Section 1: Problem Statement
    story.append(Paragraph("1. Problem Statement & Operational Objective", h1_style))
    story.append(Paragraph(
        "Automotive original equipment manufacturers (OEMs), reliability engineers, and warranty review teams "
        "monitor field quality signals to catch safety-critical component anomalies before they escalate into "
        "mandatory recalls or fleet-wide failures. The U.S. National Highway Traffic Safety Administration (NHTSA) "
        "hosts tens of thousands of owner-submitted vehicle complaints, yet this data is fundamentally messy, unstructured, "
        "and difficult for engineers to triage rapidly. Existing federal search portals require manual, one-off lookups "
        "and lack aggregated subsystem analytics.", body_style
    ))
    story.append(Paragraph(
        "<b>Core Objective:</b> Build <i>PartPulse</i> as a responsive, presentation-ready quality intelligence radar "
        "that connects to live federal databases, normalizes owner complaint filings, surfaces frequency patterns and "
        "acute safety signals (crashes, fires, injuries), and provides granular evidence drill-downs for engineering investigation.", body_style
    ))
    story.append(Spacer(1, 8))

    # Section 2: Data Architecture
    story.append(Paragraph("2. Data Architecture & Federal API Integration", h1_style))
    story.append(Paragraph(
        "PartPulse utilizes a decoupled two-tier architecture: a backend data engine (<code>data_engine.py</code>) "
        "and a reactive presentation layer (<code>app.py</code>). This separation of concerns guarantees clean testing and modularity.", body_style
    ))
    story.append(Paragraph("Key Data Engineering Components:", h2_style))
    story.append(Paragraph("• <b>Live Federal Querying & Caching:</b> Calls NHTSA's <code>complaintsByVehicle</code> REST API with vehicle Make, Model, and Year. Requests are wrapped in Streamlit's <code>@st.cache_data(ttl=3600)</code> with network retry handling, preventing redundant queries and federal server throttling.", bullet_style))
    story.append(Paragraph("• <b>NHTSA Edge-Case Handling:</b> A critical defect in standard API client integrations is handling zero results. When zero complaints match a vehicle, NHTSA's API returns HTTP 400 with a payload of <code>{'count': 0, 'results': []}</code> instead of HTTP 200. The data engine intercepts this specific status and translates it into an empty dataset rather than raising an unhandled exception.", bullet_style))
    story.append(Paragraph("• <b>Schema Normalization & Defensive Parsing:</b> Handles schema drift, null dates, masked VINs, and disparate boolean representations (e.g., parsing <code>True</code>, <code>'yes'</code>, <code>1</code>, and <code>'true'</code> for crash and fire flags into strict boolean types).", bullet_style))
    story.append(Paragraph("• <b>Atomic Component Splitting:</b> NHTSA complaints frequently group interacting assemblies into single compound strings (e.g. <i>'STEERING, SUSPENSION'</i>). PartPulse decomposes these multi-part strings into distinct atomic units so part rankings accurately reflect true mechanical subsystems.", bullet_style))
    story.append(Spacer(1, 8))

    # Section 3: Analytical Methodology
    story.append(Paragraph("3. Analytical Methodology & Explainable Metrics", h1_style))
    story.append(Paragraph(
        "In safety-critical automotive engineering, opacity is dangerous. PartPulse deliberately avoids uninterpretable "
        "'black box' models in favor of transparent, auditable mathematical metrics:", body_style
    ))
    story.append(Paragraph("• <b>Incident Signal Index (ISI):</b> Defined as <code>(Reports with Crash, Fire, or Injury / Total Reports) × 100</code>. This quantifies the concentration of acute safety events within the complaint sample.", bullet_style))
    story.append(Paragraph("• <b>The Missing Population Denominator Caveat:</b> The system explicitly warns reviewers that raw complaint counts are <i>not</i> mechanical failure rates. Public NHTSA records lack sales volumes and fleet mileage exposure. 300 complaints on a truck with 800,000 units sold represents a drastically lower true failure rate than 80 complaints on a specialty vehicle with 5,000 units sold.", bullet_style))
    story.append(Paragraph("• <b>Triangulation Role:</b> PartPulse positions public complaint data as an early detection radar to be cross-referenced with internal warranty claims (R/1000), dealer Technical Service Bulletins (TSBs), and physical teardown metallurgy.", bullet_style))
    story.append(Spacer(1, 8))

    # Section 4: Role of AI
    story.append(Paragraph("4. Role of Artificial Intelligence (Minimal & Moderate Usage)", h1_style))
    story.append(Paragraph(
        "In alignment with rigorous software engineering best practices, artificial intelligence was utilized in a "
        "<b>moderate, targeted engineering capacity</b> rather than being blindly embedded into the core logic:", body_style
    ))
    story.append(Paragraph("• <b>Used for Engineering Acceleration:</b> AI assistance was leveraged as a technical pair programmer to scaffold boilerplate data schemas, accelerate CSS layout styling, formulate regex patterns for multi-component parsing, and assist in unit test coverage design.", bullet_style))
    story.append(Paragraph("• <b>Deliberately Omitted from Diagnostics:</b> Generative AI was <i>not</i> used to diagnose mechanical defects or summarize customer narratives. LLMs can hallucinate causes, invent non-existent recalls, or misinterpret technical fault codes. In automotive quality compliance, verbatim consumer quotes and transparent statistical aggregations are strictly required.", bullet_style))
    story.append(Spacer(1, 8))

    # Section 5: Verification & Quality Assurance
    story.append(Paragraph("5. Verification, Testing & Deployment", h1_style))
    story.append(Paragraph(
        "The project was verified through a structured engineering pipeline:", body_style
    ))
    story.append(Paragraph("• <b>Automated Test Suite (<code>test_app.py</code>):</b> Unit tests cover safe type coercions, empty dataset responses, atomic component parsing, and safety index arithmetic.", bullet_style))
    story.append(Paragraph("• <b>Environmental Compatibility:</b> Diagnosed and resolved Python 3.15 C-extension compilation errors by pinning dependencies to stable Python 3.12 (supported by NumPy and Pandas binary wheels).", bullet_style))
    story.append(Paragraph("• <b>Cloud CI/CD Deployment:</b> Successfully deployed to Streamlit Community Cloud with GitHub integration. Resolved internal container port binding to ensure automated health checks pass reliably on standard port 8501.", bullet_style))
    story.append(Spacer(1, 10))

    # Conclusion Callout Box
    concl_data = [[Paragraph(
        "<b>Summary:</b> PartPulse bridges the gap between raw public federal safety records and actionable quality intelligence. "
        "Through deterministic data normalization, transparent severity metrics, interactive visualizations, and deep narrative inspection, "
        "it delivers an auditable, presentation-ready tool for automotive engineering review.", callout_style
    )]]
    concl_table = Table(concl_data, colWidths=[504])
    concl_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#E6FFFA")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#0D9488")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(concl_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated PDF: {filepath}")

if __name__ == "__main__":
    out_path = r"C:\Users\LENOVO\.gemini\antigravity\scratch\partpulse\Documentation_of_Approach_PartPulse.pdf"
    build_pdf(out_path)
