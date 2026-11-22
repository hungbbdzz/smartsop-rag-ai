"""
Script tạo các file SOP kỹ thuật bổ sung chuẩn công nghiệp:
1. SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf
2. SOP_PCB_005_Bare_Board_Cleanliness_And_Inspection.pdf
3. SOP_PRINTER_006_Stencil_Solder_Paste_Printing.pdf
4. SOP_ESD_007_Electrostatic_Discharge_Control.pdf
5. SOP_SPI_008_3D_Solder_Paste_Inspection.pdf
"""
import argparse
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

OUTPUT_DIR = Path("data/sops")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _build_styles():
    styles = getSampleStyleSheet()
    return {
        "sub_header": ParagraphStyle(
            "SubHeader",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=colors.HexColor("#64748b"),
        ),
        "title": ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=18,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=6,
        ),
        "h2": ParagraphStyle(
            "DocH2",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "DocBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#334155"),
        ),
        "cell": ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#1e293b"),
        ),
        "cell_bold": ParagraphStyle(
            "TableCellBold",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#0f172a"),
        ),
    }


def _standard_table_style():
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ])

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


def generate_sop_printer_006():
    pdf_path = OUTPUT_DIR / "SOP_PRINTER_006_Stencil_Solder_Paste_Printing.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40,
    )
    st = _build_styles()
    story = []

    story.append(Paragraph("SMART ELECTRONICS MANUFACTURING CORP - SMT PRINTING CELL", st["sub_header"]))
    story.append(Paragraph("STANDARD OPERATING PROCEDURE: STENCIL SOLDER PASTE PRINTING & WIPING", st["title"]))
    story.append(Paragraph(
        "Document Code: <b>SOP-PRINTER-006</b> | Version: 1.4 | Effective: 2026-04-01 | Equipment: DEK Horizon / MPM Momentum | Standards: IPC-7525B / J-STD-005",
        st["body"],
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("1. PURPOSE & SOLDER PASTE CONDITIONING", st["h2"]))
    story.append(Paragraph(
        "This procedure defines setup, parameter limits, and defect troubleshooting for automatic screen/stencil printing of SAC305 Type 4/Type 5 solder paste. Stencil printing accounts for over 60% of downstream reflow defects; strict adherence prevents bridging, insufficient wetting, and tombstoning.<br/>"
        "- Cold Storage & Thawing: Remove sealed solder paste jar/cartridge from 2C - 8C refrigerator at least 4 hours prior to use until stabilized at ambient 22C - 25C. Never apply external heat.<br/>"
        "- Kneading & Stencil Life: Agitate jar in planetary mixer for 90 seconds before dispensing. Paste open-time on active stencil must not exceed 8 hours (or 4 hours if ambient humidity exceeds 60% RH).",
        st["body"],
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("2. PRINTER SETUP & PROCESS PARAMETER WINDOW", st["h2"]))
    story.append(Paragraph(
        "<b>Step 1 (Stencil & Support Pin Verification):</b> Confirm stainless steel laser-cut nano-coated stencil tension is >= 35 N/cm using a tension meter at 5 points. Install dedicated rigid tooling support pins under all BGA and fine-pitch QFN footprints to prevent PCB deflection.<br/>"
        "<b>Step 2 (Zero Print Gap & Squeegee Setup):</b> Set on-contact print gap to 0.00 mm (zero snap-off). Inspect 60-degree metallic squeegee blades for nicks; set squeegee force to 4.5 - 7.0 kg (0.20 - 0.30 kg/cm of blade length), print speed to 25 - 50 mm/s, and separation speed to 0.5 - 1.5 mm/s.<br/>"
        "<b>Step 3 (Under-Stencil Wipe Protocol):</b> Configure automatic Dry-Vacuum-Solvent wipe sequence every 5 print strokes (or every 3 strokes for 0.4mm pitch BGA/CSP assemblies) using lint-free IPA wipes.",
        st["body"],
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("3. STENCIL PRINTER ALARM & DEFECT TROUBLESHOOTING MATRIX", st["h2"]))
    story.append(Paragraph("When printer machine alarms or visual paste defects occur, execute the corresponding corrective protocol:", st["body"]))
    story.append(Spacer(1, 6))

    table_data = [
        [
            Paragraph("<b>Error Code</b>", st["cell_bold"]),
            Paragraph("<b>Fault / Symptom</b>", st["cell_bold"]),
            Paragraph("<b>Root Cause Analysis</b>", st["cell_bold"]),
            Paragraph("<b>Corrective Action Protocol</b>", st["cell_bold"]),
        ],
        [
            Paragraph("<b>SP-101</b><br/>Squeegee Pressure Fault", st["cell_bold"]),
            Paragraph("Squeegee fails to reach target force or over-force alarm triggers on print stroke.", st["cell"]),
            Paragraph("Pneumatic regulator drift, bent squeegee holder, or clogged proportional valve.", st["cell"]),
            Paragraph("1. Pause cycle and inspect incoming compressed air pressure (0.50 - 0.65 MPa).<br/>2. Re-home Z-axis servo and recalibrate squeegee load cell.<br/>3. Verify PCB thickness parameter matches active recipe (+/- 0.1 mm).", st["cell"]),
        ],
        [
            Paragraph("<b>SP-105</b><br/>Vision Alignment Offset", st["cell_bold"]),
            Paragraph("2D optical fiducial recognition fails or X/Y/Theta alignment exceeds +/- 0.025 mm.", st["cell"]),
            Paragraph("Soiled fiducial marks, contaminated camera coaxial lens, or worn conveyor clamp rails.", st["cell"]),
            Paragraph("1. Clean stencil fiducials with dry ESD wipe and inspect PCB fiducial contrast.<br/>2. Blow dust off top/bottom vision camera prism.<br/>3. Re-teach fiducial lighting threshold and verify conveyor clamp flatness.", st["cell"]),
        ],
        [
            Paragraph("<b>SP-203</b><br/>Solder Paste Bridging / Slump", st["cell_bold"]),
            Paragraph("Adjacent QFP/BGA paste bricks touch or smear underneath stencil foil.", st["cell"]),
            Paragraph("Worn stencil gasketing, excessive squeegee pressure (>8 kg), or under-stencil wipe overdue.", st["cell"]),
            Paragraph("1. Trigger manual Dry-Vacuum under-stencil wipe immediately.<br/>2. Reduce squeegee pressure in 0.5 kg steps until clean foil sweep.<br/>3. Verify under-board support pins directly beneath bridged pads.<br/>4. Replace expired/slumped paste roll on stencil.", st["cell"]),
        ],
        [
            Paragraph("<b>SP-207</b><br/>Insufficient Paste / Aperture Clog", st["cell_bold"]),
            Paragraph("Incomplete brick transfer or dog-ears on 0201 passives and 0.4mm QFN apertures.", st["cell"]),
            Paragraph("Dried paste in apertures, excessively fast print speed (>60 mm/s), or paste bead < 10 mm diameter.", st["cell"]),
            Paragraph("1. Inspect stencil apertures under 20x microscope and run solvent-vacuum clean.<br/>2. Add fresh SAC305 paste to maintain a uniform 15 - 20 mm rolling paste bead.<br/>3. Lower print speed by 5 mm/s and lower stencil separation speed to 0.8 mm/s.", st["cell"]),
        ],
    ]

    t = Table(table_data, colWidths=[1.05 * inch, 1.55 * inch, 1.85 * inch, 2.85 * inch])
    t.setStyle(_standard_table_style())
    story.append(t)
    story.append(PageBreak())

    story.append(Paragraph("4. POST-PRINT INSPECTION & ESCALATION RULES", st["h2"]))
    story.append(Paragraph(
        "- First-Article Verification: Following every stencil changeover or solder paste lot change, perform 100% 3D SPI verification on the first 3 consecutive panels before releasing line to full automatic run.<br/>"
        "- Rework Policy for Misprinted PCBs: Never double-print over wet solder paste. Wash misprinted bare boards in ultrasonic DI-water + saponifier bath within 15 minutes, air-knife dry, and verify complete flux residue removal under UV light.<br/>"
        "- Shift Handover Log: Record paste lot number, ambient temperature/RH, stencil stroke counter, and wiper paper consumption in the MES station log.",
        st["body"],
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("5. SAFETY & CHEMICAL HANDLING", st["h2"]))
    story.append(Paragraph(
        "- Operators handling lead-free or tin-lead solder paste and stencil cleaner solvents must wear nitrile gloves and safety glasses.<br/>"
        "- Keep printer safety interlock covers closed during automatic print strokes; never bypass light curtains during squeegee homing.<br/>"
        "- Dispose of solder paste-contaminated wipers in designated hazardous chemical waste receptacles for metallic recycling.",
        st["body"],
    ))

    doc.build(story)
    print(f"Created: {pdf_path}")


def generate_sop_esd_007():
    pdf_path = OUTPUT_DIR / "SOP_ESD_007_Electrostatic_Discharge_Control.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40,
    )
    st = _build_styles()
    story = []

    story.append(Paragraph("SMART ELECTRONICS MANUFACTURING CORP - QUALITY & COMPLIANCE", st["sub_header"]))
    story.append(Paragraph("STANDARD OPERATING PROCEDURE: ELECTROSTATIC DISCHARGE (ESD) & MSL CONTROL", st["title"]))
    story.append(Paragraph(
        "Document Code: <b>SOP-ESD-007</b> | Version: 2.1 | Effective: 2026-04-05 | Standards: ANSI/ESD S20.20-2021 / IPC/JEDEC J-STD-033D",
        st["body"],
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("1. ESD PROTECTED AREA (EPA) MANDATORY CONTROLS", st["h2"]))
    story.append(Paragraph(
        "All SMT assembly lines, rework benches, and incoming kitting zones are designated ESD Protected Areas (EPAs) engineered to handle ESDS components sensitive down to Class 0A (< 125 V HBM / < 200 V CDM).<br/>"
        "- Personnel Grounding: Every operator entering an EPA must wear an ESD smock (buttoned over sleeves), ESD heel grounders/footwear, and a dual-wire continuous-monitored wrist strap when seated.<br/>"
        "- Resistance Limits: Wrist strap system resistance must measure 0.75 MOhm to 35 MOhm; footwear + conductive floor combined resistance must be < 35 MOhm (maximum body voltage < 100 V).<br/>"
        "- Prohibited Insulators: Non-ESD plastics, bubble wrap, cellophane tape, paper cups, and standard notebooks are strictly barred within 30 cm of exposed ESDS assemblies.",
        st["body"],
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("2. AIR IONIZATION & ENVIRONMENTAL MONITORING", st["h2"]))
    story.append(Paragraph(
        "Overhead steady-state DC benchtop and machine-internal ionizers must neutralize ungrounded process insulators (e.g., PCB FR-4 substrates, feeder carrier tapes, Teflon nozzle holders).<br/>"
        "- Ionizer Offset Voltage (Balance): Must remain within +/- 35 V measured with a charged-plate monitor (CPM) at 45 cm working distance.<br/>"
        "- Discharge Decay Time: +/- 1000 V to +/- 100 V decay must complete in <= 5.0 seconds.<br/>"
        "- Environmental Window: Maintain shop floor ambient temperature at 23C +/- 3C and Relative Humidity between 40% RH and 65% RH to suppress triboelectric charge generation.",
        st["body"],
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("3. ESD COMPLIANCE ALARMS & CORRECTIVE ACTIONS", st["h2"]))
    story.append(Paragraph("Any failed daily verification or continuous monitor alarm triggers an immediate containment response:", st["body"]))
    story.append(Spacer(1, 6))

    table_data = [
        [
            Paragraph("<b>Alarm / Code</b>", st["cell_bold"]),
            Paragraph("<b>Condition / Threshold Violation</b>", st["cell_bold"]),
            Paragraph("<b>Immediate Containment</b>", st["cell_bold"]),
            Paragraph("<b>Corrective Action & Sign-off</b>", st["cell_bold"]),
        ],
        [
            Paragraph("<b>ESD-01</b><br/>Wrist Strap High-Z / Open", st["cell_bold"]),
            Paragraph("Continuous wrist strap monitor sounds red alarm (R > 35 MOhm or R < 0.75 MOhm open/short).", st["cell"]),
            Paragraph("Stop handling PCBs immediately. Place exposed assembly inside dissipative tray.", st["cell"]),
            Paragraph("1. Check coiled cord snap connection and banana jack at station ground.<br/>2. Moisturize skin if dry or tighten conductive elastic cuff.<br/>3. Test replacement strap on combo tester before resuming work.", st["cell"]),
        ],
        [
            Paragraph("<b>ESD-02</b><br/>Ionizer Offset Drift", st["cell_bold"]),
            Paragraph("Ionizer balance exceeds +/- 35 V or red HV fault LED illuminates over pick-and-place feeder bank.", st["cell"]),
            Paragraph("Do not peel carrier cover tape at un-ionized feeder station until ionizer is restored.", st["cell"]),
            Paragraph("1. Power off ionizer and clean emitter needles with IPA swab.<br/>2. Re-measure offset balance (+/- 35 V) and decay (<= 5s) with CPM.<br/>3. Replace worn emitter pins if balance cannot be zeroed.", st["cell"]),
        ],
        [
            Paragraph("<b>ESD-03</b><br/>EPA Humidity Out-of-Range", st["cell_bold"]),
            Paragraph("Cleanroom wall hygrometer drops below 40% RH or exceeds 65% RH for > 15 minutes.", st["cell"]),
            Paragraph("If RH < 40%, halt kitting of unsealed Class 0 MOSFET/RF ICs.", st["cell"]),
            Paragraph("1. Notify Facility HVAC Engineer to adjust humidifier setpoint (target 50% RH).<br/>2. Seal open Moisture Sensitive Level (MSL 2a-5a) reels in dry MBBs with desiccant.<br/>3. Resume unsealed handling only after RH stabilizes >= 42%.", st["cell"]),
        ],
    ]

    t = Table(table_data, colWidths=[1.05 * inch, 1.85 * inch, 1.75 * inch, 2.65 * inch])
    t.setStyle(_standard_table_style())
    story.append(t)
    story.append(PageBreak())

    story.append(Paragraph("4. MOISTURE SENSITIVE DEVICE (MSD) FLOOR-LIFE CONTROL", st["h2"]))
    story.append(Paragraph(
        "Per IPC/JEDEC J-STD-033D, ICs rated MSL 2 through MSL 5a absorb ambient moisture that vaporizes during 245C reflow, causing internal package delamination ('popcorning').<br/>"
        "- Bag Opening Check: Inspect Humidity Indicator Card (HIC) immediately upon cutting a vacuum-sealed Moisture Barrier Bag. If the 10% or 5% RH spot has turned pink, quarantine the reel for dry-baking.<br/>"
        "- Exposure Tracking: Stamp the MES floor-life start timestamp on the reel barcode. Unmounted MSL 3 reels (168-hour limit) must return to < 5% RH nitrogen dry cabinets whenever idle > 2 hours.<br/>"
        "- Standard Bake Recovery: Bake compromised plastic SMD reels at 125C for 24-48 hours (high-temp trays) or 40C at <= 5% RH for 8-14 days (low-temp tape-and-reel carriers).",
        st["body"],
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("5. DAILY AUDIT & CALIBRATION RECORD", st["h2"]))
    story.append(Paragraph(
        "- Every operator must log a Pass on the wall-mounted ESD Turnstile/Combo Tester at shift start prior to badge activation.<br/>"
        "- ESD Coordinators audit work-surface mat ground resistance (1.0 MOhm to 1.0 GOhm point-to-ground) weekly and record measurements in the SmartSOP quality database.",
        st["body"],
    ))

    doc.build(story)
    print(f"Created: {pdf_path}")


def generate_sop_spi_008():
    pdf_path = OUTPUT_DIR / "SOP_SPI_008_3D_Solder_Paste_Inspection.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40,
    )
    st = _build_styles()
    story = []

    story.append(Paragraph("SMART ELECTRONICS MANUFACTURING CORP - INLINE METROLOGY", st["sub_header"]))
    story.append(Paragraph("STANDARD OPERATING PROCEDURE: 3D SOLDER PASTE INSPECTION (SPI) & SPC CONTROL", st["title"]))
    story.append(Paragraph(
        "Document Code: <b>SOP-SPI-008</b> | Version: 1.3 | Effective: 2026-04-10 | Equipment: Parmi SIGMA X 3D SPI | Standard: IPC-7527 / IPC-A-610",
        st["body"],
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("1. INLINE 3D SPI SCOPE & ACCEPTANCE WINDOWS", st["h2"]))
    story.append(Paragraph(
        "Every printed PCB assembly passes through the 3D Solder Paste Inspection (SPI) station immediately downstream of the stencil printer prior to chip mounting. Structured-light laser triangulation measures true 3D paste brick Volume, Area, Height, XY Offset, and Bridge presence.<br/>"
        "- Target Volume Window (General Passives & IC Leads): 70% to 130% of theoretical aperture volume (Warning limits: 75% / 120%).<br/>"
        "- Fine-Pitch BGA / 0.4mm QFN Volume Window: 75% to 120% with zero bridging tolerated.<br/>"
        "- Paste Height Tolerance: Nominal stencil foil thickness (typically 100 um or 120 um) +/- 25% (75 um to 150 um for 120 um foil).<br/>"
        "- Pad Alignment (XY Offset): Maximum <= 0.05 mm for standard pads and <= 0.025 mm for 0201 / 0.4mm pitch CSP pads.",
        st["body"],
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("2. CALIBRATION & CONVEYOR SETUP", st["h2"]))
    story.append(Paragraph(
        "<b>Step 1 (Calibration Target Check):</b> At the start of each shift, run the golden certified 3D step-height calibration block (100 um +/- 0.5 um). Verify height repeatability sigma < 1.0 um.<br/>"
        "<b>Step 2 (Board Warpage Compensation):</b> Enable local Z-plane warpage tracking per FOV so solder mask height variations do not skew paste volume baselines.<br/>"
        "<b>Step 3 (Closed-Loop Printer Feedback):</b> Confirm TCP/IP Closed-Loop link between Parmi SIGMA X SPI and DEK Stencil Printer is ONLINE to pass automatic X/Y/Theta fiducial drift offsets.",
        st["body"],
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("3. 3D SPI ALARM CODES & ESCALATION MATRIX", st["h2"]))
    story.append(Paragraph("When SPI halts the conveyor or raises SPC trend alerts, follow these mandatory actions:", st["body"]))
    story.append(Spacer(1, 6))

    table_data = [
        [
            Paragraph("<b>Alarm Code</b>", st["cell_bold"]),
            Paragraph("<b>SPI Defect Trigger</b>", st["cell_bold"]),
            Paragraph("<b>Probable Process Cause</b>", st["cell_bold"]),
            Paragraph("<b>Operator & Engineer Action</b>", st["cell_bold"]),
        ],
        [
            Paragraph("<b>SPI-301</b><br/>Insufficient Volume Alert", st["cell_bold"]),
            Paragraph("Paste volume < 70% on any pad, or SPC Cpk < 1.33 on 3 consecutive panels.", st["cell"]),
            Paragraph("Aperture clogging due to dried paste, low paste bead volume on stencil, or low squeegee pressure.", st["cell"]),
            Paragraph("1. Pull failed PCB from downstream buffer for wash/rework (never hand-touch up wet BGA pads).<br/>2. Trigger immediate Wet-Vacuum under-stencil clean on printer.<br/>3. Verify squeegee paste bead >= 15 mm diameter.", st["cell"]),
        ],
        [
            Paragraph("<b>SPI-302</b><br/>Excessive Volume / Bridge Risk", st["cell_bold"]),
            Paragraph("Volume > 130%, height > +30%, or detected solder paste bridge between adjacent pads.", st["cell"]),
            Paragraph("Gap between PCB and stencil during stroke, missing under-board support pins, or worn stencil bottom.", st["cell"]),
            Paragraph("1. Quarantine board immediately (100% rework wash required).<br/>2. Inspect under-board support pin placement under defective area.<br/>3. Wipe underside of stencil and reduce squeegee pressure by 0.5 kg.", st["cell"]),
        ],
        [
            Paragraph("<b>SPI-305</b><br/>Consecutive Pad Offset", st["cell_bold"]),
            Paragraph("X or Y centroid shift > 0.05 mm across entire PCB or closed-loop correction saturated.", st["cell"]),
            Paragraph("PCB rail clamping slip, dirty printer alignment camera, or stencil frame stretch/slip.", st["cell"]),
            Paragraph("1. Check closed-loop offset history on SPI SPC dashboard.<br/>2. Inspect PCB edge clamp pressure and conveyor width gauge.<br/>3. Re-zero printer fiducial offset and test 1st panel verification.", st["cell"]),
        ],
    ]

    t = Table(table_data, colWidths=[1.05 * inch, 1.6 * inch, 1.8 * inch, 2.85 * inch])
    t.setStyle(_standard_table_style())
    story.append(t)
    story.append(PageBreak())

    story.append(Paragraph("4. LINE-STOP & FALSE-CALL VERIFICATION PROTOCOL", st["h2"]))
    story.append(Paragraph(
        "- Mandatory Line-Stop Rule: Three consecutive boards failing with identical defect location (`SPI-301` or `SPI-302`) automatically lock the downstream conveyor and require Shift Engineer sign-off.<br/>"
        "- False-Call Audit: Operators may re-verify flagged pads at the Review Station under 20x optical overlay. True solder bridges on IC/BGA footprints can never be overridden as Pass.<br/>"
        "- Zero-Pass Bypass Prohibition: Disabling SPI bypass switch or widening Pass/Fail tolerances below IPC-7527 limits without Engineering Change Notice (ECN) is strictly prohibited.",
        st["body"],
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("5. DATA RETENTION & TRACEABILITY", st["h2"]))
    story.append(Paragraph(
        "- Barcode scanner captures PCB Panel Serial ID prior to inspection; 3D inspection maps and volume CSV logs are archived to MES for 5 years.<br/>"
        "- Weekly Gage R&R study (target GR&R < 10%) is scheduled every Sunday night during preventive maintenance window.",
        st["body"],
    ))

    doc.build(story)
    print(f"Created: {pdf_path}")


def main(regenerate_existing: bool = False):
    targets = [
        ("SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf", generate_sop_feeder_004),
        ("SOP_PCB_005_Bare_Board_Cleanliness_And_Inspection.pdf", generate_sop_pcb_005),
        ("SOP_PRINTER_006_Stencil_Solder_Paste_Printing.pdf", generate_sop_printer_006),
        ("SOP_ESD_007_Electrostatic_Discharge_Control.pdf", generate_sop_esd_007),
        ("SOP_SPI_008_3D_Solder_Paste_Inspection.pdf", generate_sop_spi_008),
    ]
    for filename, generator in targets:
        pdf_path = OUTPUT_DIR / filename
        if regenerate_existing or not pdf_path.exists():
            generator()
        else:
            print(f"Skipped existing: {pdf_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate standardized SMT factory SOP PDFs.")
    parser.add_argument("--all", action="store_true", help="Regenerate existing PDFs as well as missing ones.")
    args = parser.parse_args()
    main(regenerate_existing=args.all)

