# Industrial SOP & Technical Manual Dataset

This directory contains SMT (Surface-Mount Technology) manufacturing manuals, semiconductor package assembly application notes, inline inspection research papers, and standardized operating procedures used for developing and evaluating SmartSOP AI's PDF ingestion and RAG pipeline.

**Corpus Summary:** `15 PDFs` | `155 pages` | `97 extracted Markdown tables` | `642 Table-Aware chunks` | `14.91 MB`

---

## 1. Public Manufacturer Manuals & Technical Application Notes (5 PDFs, 127 pages)

1. **[`T962A_Infrared_Reflow_Oven_Official_Manual.pdf`](./T962A_Infrared_Reflow_Oven_Official_Manual.pdf)** *(6 pages)*
   * **Source:** Puhui Technology T-962A Desktop Infrared IC Heater Official User Manual.
   * **Content:** Hardware specifications (1500 W, 300 x 320 mm soldering area), 8 thermal wave profiles (Wave 1–8), operating steps, and maintenance instructions.
2. **[`NXP_AN10365_Surface_Mount_Reflow_Soldering.pdf`](./NXP_AN10365_Surface_Mount_Reflow_Soldering.pdf)** *(31 pages)*
   * **Source:** NXP Semiconductors Application Note `AN10365` (Rev. 8) — [`AN10365.pdf`](https://www.nxp.com/docs/en/application-note/AN10365.pdf).
   * **Content:** Lead-free and SnPb reflow soldering profiles, moisture sensitivity handling, wave/reflow thermal tolerances, PCB pad recommendations, and rework procedures.
3. **[`TI_SLUA271C_QFN_SON_PCB_Attachment_Guidelines.pdf`](./TI_SLUA271C_QFN_SON_PCB_Attachment_Guidelines.pdf)** *(21 pages)*
   * **Source:** Texas Instruments Application Note `SLUA271C` — [`slua271`](https://www.ti.com/lit/pdf/slua271).
   * **Content:** QFN and SON package PCB land patterns, stencil aperture design, solder paste deposition ratios, reflow optimization, and X-ray voiding inspection.
4. **[`TI_SLOA122_QFN_Layout_And_Assembly_Guidelines.pdf`](./TI_SLOA122_QFN_Layout_And_Assembly_Guidelines.pdf)** *(7 pages)*
   * **Source:** Texas Instruments Application Report `SLOA122` — [`sloa122`](https://www.ti.com/lit/pdf/sloa122).
   * **Content:** Exposed thermal pad design, via-in-pad constraints, solder mask opening tolerances, and stencil segmentation for QFN power packages.
5. **[`TI_SPRAA99_BGA_SMT_Guidelines.pdf`](./TI_SPRAA99_BGA_SMT_Guidelines.pdf)** *(62 pages)*
   * **Source:** Texas Instruments Application Report `SPRAA99` — [`spraa99`](https://www.ti.com/lit/pdf/spraa99).
   * **Content:** Comprehensive nFBGA SMT assembly reference covering substrate design, solder ball alloy composition, stencil printing, pick-and-place accuracy, convection reflow profiling, and board-level reliability.

---

## 2. Open-Access SMT Inspection Research Papers (2 PDFs, 14 pages)

1. **[`Research_Paper_SMT_Inspection_DVQI_2312.09232.pdf`](./Research_Paper_SMT_Inspection_DVQI_2312.09232.pdf)** *(8 pages)*
   * **Source:** arXiv preprint `2312.09232 [cs.CV]` — [`arXiv:2312.09232`](https://arxiv.org/pdf/2312.09232) — *"DVQI: A Multi-task, Hardware-integrated Artificial Intelligence System for Automated Visual Inspection in Electronics Manufacturing"*.
   * **Content:** Computer vision defect classification and inline SMT automated visual inspection benchmarks.
2. **[`Research_Paper_SPI_PCB_Defect_Detection_2309.03113.pdf`](./Research_Paper_SPI_PCB_Defect_Detection_2309.03113.pdf)** *(6 pages)*
   * **Source:** arXiv preprint `2309.03113` — [`arXiv:2309.03113`](https://arxiv.org/pdf/2309.03113) — *"Detecting Manufacturing Defects in PCBs via Data-Centric Machine Learning on Solder Paste Inspection Features"*.
   * **Content:** Inline 3D SPI pin-level feature analysis and predictive defect detection across SMT assembly stages.

---

## 3. Standardized SMT Factory SOPs (8 PDFs, 14 pages)

Eight structured factory SOP PDFs modeled on **IPC-A-610**, **IPC-A-600J**, **IPC-7525B**, **IPC-7527**, **ANSI/ESD S20.20**, and **IPC/JEDEC J-STD-033D**, featuring structured alarm/defect Markdown-parseable matrices and step-by-step corrective actions:

1. **[`SOP_SMT_001_Pick_And_Place_Machine_Troubleshooting.pdf`](./SOP_SMT_001_Pick_And_Place_Machine_Troubleshooting.pdf)** (`SOP-SMT-FUJI-001`, 2 pages)
   * High-speed SMT pick-and-place troubleshooting (`E-101`, `E-104`, `E-112`, `E-205`), with a cross-page error matrix.
2. **[`SOP_REFLOW_002_Reflow_Soldering_Defects_Remedies.pdf`](./SOP_REFLOW_002_Reflow_Soldering_Defects_Remedies.pdf)** (`SOP-REFLOW-002`, 2 pages)
   * Reflow thermal profile requirements and remedies for Tombstoning, Solder Balling, Solder Bridging, and BGA/QFN Voiding.
3. **[`SOP_AOI_003_Automated_Optical_Inspection_Standards.pdf`](./SOP_AOI_003_Automated_Optical_Inspection_Standards.pdf)** (`SOP-AOI-003`, 1 page)
   * Post-reflow 3D AOI inspection criteria (IPC-A-610 Class 3) and line-stop escalation rules.
4. **[`SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf`](./SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf)** (`SOP-FEEDER-004-VN`, 2 pages)
   * Electric tape feeder setup, preventive maintenance, and troubleshooting matrix (`E-204`, `E-201`, `E-208`).
5. **[`SOP_PCB_005_Bare_Board_Cleanliness_And_Inspection.pdf`](./SOP_PCB_005_Bare_Board_Cleanliness_And_Inspection.pdf)** (`SOP-PCB-005-VN`, 1 page)
   * Incoming bare PCB cleanliness and inspection matrix (`PCB-D01`, `PCB-D02`, `PCB-D03`) and baking profiles.
6. **[`SOP_PRINTER_006_Stencil_Solder_Paste_Printing.pdf`](./SOP_PRINTER_006_Stencil_Solder_Paste_Printing.pdf)** (`SOP-PRINTER-006`, 2 pages)
   * Stencil solder paste conditioning, squeegee parameters, under-stencil wipe protocol, and troubleshooting (`SP-101`, `SP-105`, `SP-203`, `SP-207`).
7. **[`SOP_ESD_007_Electrostatic_Discharge_Control.pdf`](./SOP_ESD_007_Electrostatic_Discharge_Control.pdf)** (`SOP-ESD-007`, 2 pages)
   * EPA grounding, continuous monitoring, air ionization limits, MSL/MBB handling, and alarm response (`ESD-01`, `ESD-02`, `ESD-03`).
8. **[`SOP_SPI_008_3D_Solder_Paste_Inspection.pdf`](./SOP_SPI_008_3D_Solder_Paste_Inspection.pdf)** (`SOP-SPI-008`, 2 pages)
   * 3D SPI volume/area/height inspection limits, closed-loop printer feedback, and SPC alarms (`SPI-301`, `SPI-302`, `SPI-305`).

See [PROVENANCE.md](./PROVENANCE.md) for full provenance, size/chunk metrics, and ingestion testing notes.
