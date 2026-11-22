"""
Script tạo 2 file SOP kỹ thuật bổ sung chuẩn công nghiệp (SMT Feeder Setup & PCB Inspection):
1. SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf
2. SOP_PCB_005_Bare_Board_Cleanliness_And_Inspection.pdf
"""
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

OUTPUT_DIR = Path("data/sops")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_sop_feeder_004():
    pdf_path = OUTPUT_DIR / "SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=6
    )
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155")
    )
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1e293b")
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0f172a")
    )

    story = []

    # Header
    story.append(Paragraph("SMART ELECTRONICS MANUFACTURING CORP - SMT PRODUCTION DIVISION", ParagraphStyle('SubHeader', fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor("#64748b"))))
    story.append(Paragraph("STANDARD OPERATING PROCEDURE: FEEDER TAPE & REEL SETUP AND CALIBRATION", title_style))
    story.append(Paragraph("Document Code: <b>SOP-FEEDER-004-VN</b> | Version: 2.0 | Effective: 2026-03-01 | Scope: SMT Mounter Feeders (W08b, W12, W16, W24)", body_style))
    story.append(Spacer(1, 10))

    # Section 1
    story.append(Paragraph("1. PURPOSE & PRINCIPLE OF OPERATION", h2_style))
    story.append(Paragraph(
        "This standard procedure governs the mechanical alignment, peeling tension adjustment, and reel loading criteria for intelligent electric tape feeders on high-speed SMT pick-and-place lines. Proper setup eliminates pickup reject errors, component rotation misalignments, and catastrophic tape jams.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # Section 2
    story.append(Paragraph("2. FEEDER REEL LOADING STEP-BY-STEP WORKFLOW", h2_style))
    story.append(Paragraph(
        "<b>Step 1:</b> Inspect component reel label against the active Manufacturing Execution System (MES) Bill of Materials (BOM). Confirm part number, lot number, and component polarity orientation.<br/>"
        "<b>Step 2:</b> Mount reel onto feeder spool spindle. Thread carrier tape over the drive sprocket teeth, ensuring pin engagement into carrier tape indexing holes.<br/>"
        "<b>Step 3:</b> Peel back approximately 100mm of top cover film tape. Route film through the tension roller guide into the waste take-up reel spindle.<br/>"
        "<b>Step 4:</b> Set pitch toggle switch to 2mm or 4mm based on component pocket pitch specification.<br/>"
        "<b>Step 5:</b> Insert feeder cart into machine slot until latch clicks. Verify green communication LED illuminates steady.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # Section 3: Bảng mã lỗi chứa E-204
    story.append(Paragraph("3. FEEDER TROUBLESHOOTING & ALARM CODES TABLE", h2_style))
    story.append(Paragraph("When an alarm triggers during pickup cycle, consult the following diagnostic matrix immediately:", body_style))
    story.append(Spacer(1, 6))

    table_data = [
        [
            Paragraph("<b>Error Code</b>", table_cell_bold),
            Paragraph("<b>Description / Root Cause</b>", table_cell_bold),
            Paragraph("<b>Step-by-Step Corrective Action</b>", table_cell_bold),
            Paragraph("<b>Severity</b>", table_cell_bold),
        ],
        [
            Paragraph("<b>E-204</b><br/>Feeder Jam / Pickup Reject", table_cell_bold),
            Paragraph("Carrier cover film broke, tape sprocket jammed, or feeder motor torque exceeded safety threshold (>1.2 Nm).", table_cell),
            Paragraph("1. Press Yellow Pause button on SMT head.<br/>2. Disengage feeder latch and inspect tape guide channel.<br/>3. Clear sheared cover tape using anti-static ESD tweezers.<br/>4. Re-thread carrier film into tension wheel.<br/>5. Run Feeder Feed Test on HMI screen.<br/>6. Resume production run.", table_cell),
            Paragraph("High", table_cell),
        ],
        [
            Paragraph("<b>E-201</b><br/>Feeder ID Comm Error", table_cell_bold),
            Paragraph("Dirty contact pins between feeder base plate and machine interface rail.", table_cell),
            Paragraph("1. Pull feeder out of slot.<br/>2. Clean spring contact gold pins using isopropyl alcohol (IPA) swab.<br/>3. Re-seat firmly into cart slot until locked.", table_cell),
            Paragraph("Medium", table_cell),
        ],
        [
            Paragraph("<b>E-208</b><br/>Component Pitch Offset", table_cell_bold),
            Paragraph("Tape pitch selector switch set to 4mm instead of 2mm for micro-chip 0201/0402.", table_cell),
            Paragraph("1. Verify reel pocket pitch specification on reel packaging.<br/>2. Toggle pitch selector switch to correct pitch index.<br/>3. Advance 3 empty pockets to sync index.", table_cell),
            Paragraph("High", table_cell),
        ]
    ]

    t = Table(table_data, colWidths=[1.1*inch, 2.0*inch, 3.4*inch, 0.8*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # Page break for Page 2
    story.append(PageBreak())

    story.append(Paragraph("4. FEEDER CALIBRATION & PREVENTIVE MAINTENANCE SCHEDULE", h2_style))
    story.append(Paragraph(
        "<b>Daily Inspection (Per Shift):</b> Clean feeder pickup window using soft ESD brush. Check reel tension regulator spring mechanism. Wipe optical sensors.<br/>"
        "<b>Monthly Maintenance:</b> Mount feeder on offline calibration jig. Verify pickup pocket center coordinate within +/- 0.03mm tolerance. Check gear backlash.<br/>"
        "<b>Semi-Annual Overhaul:</b> Disassemble gear drive train, clean and lubricate with synthetic grease Kluber NCA 52. Replace worn guide pins.",
        body_style
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("5. SAFETY & ESD PRECAUTIONS", h2_style))
    story.append(Paragraph(
        "- Operators must wear grounded wrist straps or ESD footwear with conductive floor mat at all times.<br/>"
        "- Never insert fingers or tools into feeder gear mechanism while machine is in RUN mode.<br/>"
        "- Do not carry feeders by the tape guide plate; always use the integrated ergonomic carrying handle.",
        body_style
    ))

    doc.build(story)
    print(f"Created: {pdf_path}")

def generate_sop_pcb_005():
    pdf_path = OUTPUT_DIR / "SOP_PCB_005_Bare_Board_Cleanliness_And_Inspection.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=6
    )
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155")
    )
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1e293b")
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0f172a")
    )

    story = []

    # Header
    story.append(Paragraph("SMART ELECTRONICS MANUFACTURING CORP - QUALITY ASSURANCE DEPT", ParagraphStyle('SubHeader', fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor("#64748b"))))
    story.append(Paragraph("STANDARD OPERATING PROCEDURE: BARE PCB CLEANLINESS & INCOMING QUALITY CONTROL", title_style))
    story.append(Paragraph("Document Code: <b>SOP-PCB-005-VN</b> | Version: 1.2 | Effective: 2026-03-15 | Standards: IPC-A-600J / IPC-6012E Class 3", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("1. SCOPE & ACCEPTANCE CRITERIA", h2_style))
    story.append(Paragraph(
        "This standard operating procedure defines incoming quality inspection criteria, surface cleanliness verification, and vacuum packaging storage standards for multi-layer bare Printed Circuit Boards (PCBs) before introduction to high-precision SMT solder paste printing.",
        body_style
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("2. PCB SURFACE DEFECT CLASSIFICATION MATRIX", h2_style))
    story.append(Paragraph("Incoming bare boards must be evaluated against the following visual inspection standards:", body_style))
    story.append(Spacer(1, 6))

    table_data = [
        [
            Paragraph("<b>Defect Code</b>", table_cell_bold),
            Paragraph("<b>Defect Name / Description</b>", table_cell_bold),
            Paragraph("<b>Quality Standard (IPC Class 3)</b>", table_cell_bold),
            Paragraph("<b>Disposition Action</b>", table_cell_bold),
        ],
        [
            Paragraph("<b>PCB-D01</b><br/>Pad Oxidation", table_cell_bold),
            Paragraph("ENIG / OSP surface pad discolored or oxidized causing poor solder wetting.", table_cell),
            Paragraph("Zero discoloration permitted on QFN/BGA contact pads under 10x magnification.", table_cell),
            Paragraph("Reject lot. Return to PCB fabricator.", table_cell),
        ],
        [
            Paragraph("<b>PCB-D02</b><br/>Substrate Warpage", table_cell_bold),
            Paragraph("Board bow or twist exceeding flatness limits for SMT automated conveyor.", table_cell),
            Paragraph("Bow & Twist must be <= 0.75% of diagonal dimension (<= 0.5% for 0.4mm pitch BGA).", table_cell),
            Paragraph("Quarantine lot. Perform pre-bake at 120C for 4 hours.", table_cell),
        ],
        [
            Paragraph("<b>PCB-D03</b><br/>Fiducial Scratch", table_cell_bold),
            Paragraph("Optical fiducial target copper mark abraded, scratched or solder mask encroached.", table_cell),
            Paragraph("Fiducial diameter 1.0mm +/- 0.05mm must be 100% complete and unobstructed.", table_cell),
            Paragraph("Reject board. Mark with red tag.", table_cell),
        ]
    ]

    t = Table(table_data, colWidths=[1.1*inch, 1.8*inch, 2.8*inch, 1.6*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("3. MOISTURE SENSITIVITY & BAKING PROCEDURE", h2_style))
    story.append(Paragraph(
        "- PCBs stored in unsealed Moisture Barrier Bags (MBB) exceeding 72 hours floor life must undergo pre-baking.<br/>"
        "- Baking profile: Bake at 105C - 125C for a duration of 4 to 8 hours in an ESD-safe baking oven.<br/>"
        "- After baking, transfer boards to nitrogen storage cabinet (Relative Humidity < 5%) within 30 minutes.",
        body_style
    ))

    doc.build(story)
    print(f"Created: {pdf_path}")

if __name__ == "__main__":
    generate_sop_feeder_004()
    generate_sop_pcb_005()

