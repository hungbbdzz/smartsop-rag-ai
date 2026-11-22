import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sops")
os.makedirs(out_dir, exist_ok=True)

styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    fontSize=18,
    leading=22,
    textColor=colors.HexColor('#0f2b5c'),
    alignment=1, # Center
    spaceAfter=12
)
subtitle_style = ParagraphStyle(
    'DocSubTitle',
    parent=styles['Normal'],
    fontSize=10,
    leading=14,
    textColor=colors.HexColor('#555555'),
    alignment=1,
    spaceAfter=20
)
h2_style = ParagraphStyle(
    'DocH2',
    parent=styles['Heading2'],
    fontSize=13,
    leading=16,
    textColor=colors.HexColor('#1a5fb4'),
    spaceBefore=14,
    spaceAfter=8
)
body_style = ParagraphStyle(
    'DocBody',
    parent=styles['Normal'],
    fontSize=9.5,
    leading=14,
    textColor=colors.HexColor('#222222'),
    spaceAfter=6
)
code_style = ParagraphStyle(
    'DocCode',
    parent=styles['Normal'],
    fontName='Courier-Bold',
    fontSize=9,
    leading=12,
    textColor=colors.HexColor('#b31d28')
)

# ----------------- DOC 1: SMT Pick and Place Machine SOP -----------------
doc1_path = os.path.join(out_dir, "SOP_SMT_001_Pick_And_Place_Machine_Troubleshooting.pdf")
doc1 = SimpleDocTemplate(doc1_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
story1 = []

story1.append(Paragraph("SMART ELECTRONICS MANUFACTURING CORP - SMT DIVISION", subtitle_style))
story1.append(Paragraph("STANDARD OPERATING PROCEDURE: SMT HIGH-SPEED PICK & PLACE SYSTEM", title_style))
story1.append(Paragraph("Document ID: <b>SOP-SMT-FUJI-001</b> | Rev: 3.2 | Effective Date: 2026-01-15 | Scope: Surface Mount Line 1-4", subtitle_style))
story1.append(Spacer(1, 10))

story1.append(Paragraph("1. PURPOSE & OBJECTIVES", h2_style))
story1.append(Paragraph("This procedure defines the standard operating criteria, safety protocols, and systematic troubleshooting steps for operating High-Speed Surface Mount Technology (SMT) Pick and Place machines (compatible with Fuji NXT, Yamaha YSM20R, and Panasonic NPM-D3 series). The primary goal is to minimize line downtime and maintain component placement accuracy under 15 microns.", body_style))

story1.append(Paragraph("2. PERSONAL PROTECTIVE EQUIPMENT (PPE) & ESD PROTOCOLS", h2_style))
story1.append(Paragraph("All technicians and line operators entering the SMT Cleanroom Zone must strictly comply with ISO 14644-1 Class 10,000 cleanroom requirements:", body_style))
story1.append(Paragraph("• <b>Electrostatic Discharge (ESD) Wrist Strap:</b> Must be plugged into the grounded terminal and tested daily with resistance between 0.75MΩ and 35MΩ.<br/>• <b>Conductive Smock & ESD Safety Shoes:</b> Mandatory across all active conveyor zones.<br/>• <b>Anti-static Nitrile Gloves:</b> Required when handling PCB substrates, nozzles, and tape feeders.", body_style))

story1.append(Paragraph("3. SYSTEM ERROR CODE MATRIX & CORRECTIVE ACTION PROCEDURES", h2_style))
story1.append(Paragraph("When an alarm triggers, refer immediately to the numeric code displayed on the HMI console:", body_style))

data1 = [
    [Paragraph("<b>Error Code</b>", body_style), Paragraph("<b>Description / Root Cause</b>", body_style), Paragraph("<b>Step-by-Step Corrective Action</b>", body_style), Paragraph("<b>Severity</b>", body_style)],
    [
        Paragraph("<b>E-101</b><br/>Feeder Jam", code_style),
        Paragraph("Tape feeder tape peeling film broke or tape sprocket misaligned.", body_style),
        Paragraph("1. Press Yellow Pause button.<br/>2. Open feeder latch and pull out reel.<br/>3. Clear peeled plastic film with anti-static tweezers.<br/>4. Re-thread carrier tape into guide sprocket and re-lock latch.<br/>5. Press Resume.", body_style),
        Paragraph("Medium", body_style)
    ],
    [
        Paragraph("<b>E-104</b><br/>Nozzle Vacuum Drop", code_style),
        Paragraph("Suction nozzle tip clogged with solder dust or rubber tip degraded (Vacuum < -65 kPa).", body_style),
        Paragraph("1. Stop head via Pause button.<br/>2. Inspect Nozzle Head #3 and #7 using optical magnifier.<br/>3. Clean orifice with isopropyl alcohol (IPA) ultrasonic cleaner for 3 mins.<br/>4. If tip is chipped, replace nozzle from Station Spare Rack.<br/>5. Run Vacuum Self-Test calibration.", body_style),
        Paragraph("High", body_style)
    ],
    [
        Paragraph("<b>E-112</b><br/>Fiducial Recognition Failed", code_style),
        Paragraph("PCB substrate fiducial mark oxidized, scratched, or camera lens smudged.", body_style),
        Paragraph("1. Inspect bottom camera ring light illumination intensity.<br/>2. Clean downward-looking camera optical lens with micro-fiber cloth.<br/>3. Verify PCB panel positioning clamps have 0.5mm clearance.<br/>4. Re-teach Mark 1 & Mark 2 coordinates on HMI vision calibration page.", body_style),
        Paragraph("Critical", body_style)
    ],
    [
        Paragraph("<b>E-205</b><br/>Component Pick Offset", code_style),
        Paragraph("High component drop rate (>0.05%) due to pocket vibration or feeder pitch mismatch.", body_style),
        Paragraph("1. Check reel tension regulator spring.<br/>2. Re-teach pickup height in increments of -0.05mm.<br/>3. Verify component library dimensions (Length, Width, Thickness) match current bill of materials (BOM).", body_style),
        Paragraph("High", body_style)
    ]
]

t1 = Table(data1, colWidths=[1.1*inch, 2.0*inch, 3.2*inch, 0.9*inch])
t1.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e8f0fe')),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#bbbbbb')),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ('TOPPADDING', (0,0), (-1,-1), 6),
]))
story1.append(t1)

story1.append(Spacer(1, 14))
story1.append(Paragraph("4. DAILY PREVENTIVE MAINTENANCE CHECKLIST", h2_style))
story1.append(Paragraph("• <b>Shift Handover (Every 8 Hours):</b> Empty trash tape bin, check pneumatic air pressure (0.50 ± 0.05 MPa), verify optical recognition score > 85%.<br/>• <b>Weekly Calibration:</b> Clean linear guide rails and apply Kluber NCA 52 grease. Perform Auto-Tool Changer (ATC) position check.", body_style))

doc1.build(story1)

# ----------------- DOC 2: Reflow Oven Troubleshooting Guide -----------------
doc2_path = os.path.join(out_dir, "SOP_REFLOW_002_Reflow_Soldering_Defects_Remedies.pdf")
doc2 = SimpleDocTemplate(doc2_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
story2 = []

story2.append(Paragraph("SMART ELECTRONICS MANUFACTURING CORP - SMT DIVISION", subtitle_style))
story2.append(Paragraph("STANDARD OPERATING PROCEDURE: REFLOW SOLDERING PROCESS DEFECT REMEDIES", title_style))
story2.append(Paragraph("Document ID: <b>SOP-REFLOW-002</b> | Rev: 4.0 | Applicable Standards: IPC-A-610 Class 3 / J-STD-001", subtitle_style))
story2.append(Spacer(1, 10))

story2.append(Paragraph("1. PROCESS OVERVIEW & THERMAL PROFILE REQUIREMENTS", h2_style))
story2.append(Paragraph("Reflow soldering is the critical phase where printed solder paste is liquefied and cooled to establish electrical and mechanical joints. For lead-free alloys (SAC305 - Sn96.5 Ag3.0 Cu0.5), the oven must strictly adhere to the 4-stage thermal specification:", body_style))
story2.append(Paragraph("• <b>Preheat Zone (Ramp Rate 1.5 - 2.5 °C/sec):</b> Raise board temperature to 150 °C.<br/>• <b>Soak Zone (150 °C - 190 °C for 60 - 90s):</b> Activate flux, evaporate solvents, equalize thermal mass.<br/>• <b>Reflow Peak Zone (Peak Temp 238 °C - 245 °C, Time Above Liquidus TAL 45 - 65s):</b> Complete wetting of solder alloy.<br/>• <b>Cooling Zone (Cooling Rate 2.0 - 4.0 °C/sec):</b> Rapid grain structure formation.", body_style))

story2.append(Paragraph("2. COMMON DEFECT ROOT-CAUSE & TROUBLESHOOTING MATRIX", h2_style))

data2 = [
    [Paragraph("<b>Defect Name</b>", body_style), Paragraph("<b>Physical Mechanism & Root Cause</b>", body_style), Paragraph("<b>Corrective Remediation Protocol</b>", body_style)],
    [
        Paragraph("<b>Tombstoning</b><br/>(Manhattan Effect)", code_style),
        Paragraph("Unequal surface tension forces between component terminals during reflow; one pad melts before the other due to uneven thermal dissipation.", body_style),
        Paragraph("1. Extend Soak Zone time by +10 seconds to equalize pad temperatures.<br/>2. Reduce ramp-up rate entering liquidus zone to < 2.0 °C/s.<br/>3. Verify stencil aperture equal area on both pads.<br/>4. Check placement accuracy: component center must not deviate > 0.05mm from pad center.", body_style)
    ],
    [
        Paragraph("<b>Solder Balling & Beading</b>", code_style),
        Paragraph("Excessive solder paste volume squeezed under component body; rapid flux outgassing causing solder spattering.", body_style),
        Paragraph("1. Inspect stencil squeegee pressure (standard: 0.22 kg/cm).<br/>2. Implement 'Home-Plate' or inverted aperture cutout design on 0603/0402 passives.<br/>3. Increase preheat temperature by 5 °C to drive off volatile solvents gently.", body_style)
    ],
    [
        Paragraph("<b>Solder Bridging</b><br/>(Short Circuit)", code_style),
        Paragraph("Excess paste deposition, solder slump, or fine-pitch QFP/BGA pad misalignment.", body_style),
        Paragraph("1. Increase stencil underside automatic wipe frequency from every 5 boards to every 2 boards.<br/>2. Replace solder paste if expired (room temperature life > 8 hours without replenishment).<br/>3. Check reflow oven conveyor vibration: verify chain tension.", body_style)
    ],
    [
        Paragraph("<b>Voiding in BGA/QFN</b>", code_style),
        Paragraph("Entrapped gas volatiles under thermal pads exceeding IPC Class 3 limit (> 25% area).", body_style),
        Paragraph("1. Extend time above liquidus (TAL) to 65 seconds to allow outgassing.<br/>2. Switch stencil aperture on large thermal pads to window-pane grid (4 to 9 squares).<br/>3. Enable nitrogen (N2) atmosphere: ensure O2 level < 500 ppm.", body_style)
    ]
]

t2 = Table(data2, colWidths=[1.4*inch, 2.7*inch, 3.1*inch])
t2.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#fce8e6')),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#bbbbbb')),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ('TOPPADDING', (0,0), (-1,-1), 6),
]))
story2.append(t2)

doc2.build(story2)

# ----------------- DOC 3: AOI Quality Inspection Standards -----------------
doc3_path = os.path.join(out_dir, "SOP_AOI_003_Automated_Optical_Inspection_Standards.pdf")
doc3 = SimpleDocTemplate(doc3_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
story3 = []

story3.append(Paragraph("SMART ELECTRONICS MANUFACTURING CORP - SMT DIVISION", subtitle_style))
story3.append(Paragraph("STANDARD OPERATING PROCEDURE: POST-REFLOW AOI QUALITY CRITERIA & ESCALATION", title_style))
story3.append(Paragraph("Document ID: <b>SOP-AOI-003</b> | Rev: 2.5 | Line: SMT High-Density Boards QA Zone", subtitle_style))
story3.append(Spacer(1, 10))

story3.append(Paragraph("1. SCOPE & INSPECTION WORKFLOW", h2_style))
story3.append(Paragraph("This procedure outlines the criteria for automated optical inspection (AOI) post-reflow soldering. Every assembled PCB panel must undergo 100% 3D AOI inspection prior to in-circuit testing (ICT) and final packaging.", body_style))

story3.append(Paragraph("2. ACCEPTANCE CRITERIA ACCORDING TO IPC-A-610 CLASS 3", h2_style))
story3.append(Paragraph("• <b>Component Alignment:</b> Maximum allowable lateral overhang must not exceed 25% of component termination width.<br/>• <b>Minimum Solder Fillet Height:</b> Solder fillet must reach at least 50% of the termination height + 0.15mm.<br/>• <b>Polarity & Marking:</b> Diodes, IC Pin 1 markings, and electrolytic capacitors must match silk-screen polarity 100%. Reversed polarity is classified as Critical Defect.", body_style))

story3.append(Paragraph("3. ESCALATION & LINE SHUTDOWN PROTOCOL", h2_style))
story3.append(Paragraph("If the same defect occurs <b>3 consecutive times</b> on the same component location across successive panels, or if the hourly defect rate exceeds <b>0.15%</b>:", body_style))
story3.append(Paragraph("1. <b>Immediate Action:</b> AOI operator triggers emergency line pause buzzer.<br/>2. <b>Containment:</b> Quarantine all panels produced within the last 30 minutes in the Yellow Review Bin.<br/>3. <b>Ticket Generation:</b> File an Urgent Incident Ticket in the Smart Factory Web System citing machine ID and feeder slot.<br/>4. <b>Notification:</b> Shift QA Engineer and SMT Process Lead must inspect the printer/placer within 5 minutes.", body_style))

doc3.build(story3)
print("Successfully generated 3 SOP PDF files in:", out_dir)
