# Dataset Provenance & Technical Overview

This file documents the origin, structure, and ingestion test characteristics of the 15 PDF documents in `data/sops/`.

**Verified Corpus Totals (`parse_pdf_document` + `TableAwareChunker`):**
- **Total Documents:** 15 PDFs (7 public external references + 8 standardized factory SOPs)
- **Total Pages:** 155 pages (minimum extracted text density: 102 characters/page, 0 empty pages)
- **Total Markdown Tables Extracted:** 97 tables
- **Total Semantic + Table-Aware Chunks:** 642 chunks
- **Total Size on Disk:** 14.91 MB

---

## 1. Document Inventory

| # | File Name | Document Code | Pages | Tables | Chunks | Category | Key Technical Focus |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| 1 | `SOP_SMT_001_Pick_And_Place_Machine_Troubleshooting.pdf` | `SOP-SMT-FUJI-001` | 2 | 2 | 5 | Standardized SOP | Pick-and-place error matrix (`E-101`, `E-104`, `E-112`, `E-205`), preventive maintenance |
| 2 | `SOP_REFLOW_002_Reflow_Soldering_Defects_Remedies.pdf` | `SOP-REFLOW-002` | 2 | 2 | 4 | Standardized SOP | Reflow thermal profiles, Tombstoning, Solder Balling, Bridging, BGA Voiding |
| 3 | `SOP_AOI_003_Automated_Optical_Inspection_Standards.pdf` | `SOP-AOI-003` | 1 | 0 | 3 | Standardized SOP | Post-reflow 3D AOI criteria (IPC-A-610 Class 3) & escalation protocol |
| 4 | `SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf` | `SOP-FEEDER-004-VN` | 2 | 1 | 6 | Standardized SOP | Feeder reel loading, calibration, alarm codes (`E-204`, `E-201`, `E-208`) |
| 5 | `SOP_PCB_005_Bare_Board_Cleanliness_And_Inspection.pdf` | `SOP-PCB-005-VN` | 1 | 1 | 3 | Standardized SOP | Bare PCB defect matrix (`PCB-D01`–`PCB-D03`), moisture sensitivity & baking |
| 6 | `SOP_PRINTER_006_Stencil_Solder_Paste_Printing.pdf` | `SOP-PRINTER-006` | 2 | 1 | 8 | Standardized SOP | Stencil printer setup, paste conditioning, alarm codes (`SP-101`, `SP-105`, `SP-203`, `SP-207`) |
| 7 | `SOP_ESD_007_Electrostatic_Discharge_Control.pdf` | `SOP-ESD-007` | 2 | 1 | 6 | Standardized SOP | EPA grounding, ionizers, MSL control, alarm codes (`ESD-01`–`ESD-03`) |
| 8 | `SOP_SPI_008_3D_Solder_Paste_Inspection.pdf` | `SOP-SPI-008` | 2 | 1 | 6 | Standardized SOP | 3D SPI thresholds, closed-loop printer feedback, alarms (`SPI-301`, `SPI-302`, `SPI-305`) |
| 9 | `T962A_Infrared_Reflow_Oven_Official_Manual.pdf` | `MANUAL-PUHUI-T962A` | 6 | 0 | 16 | Manufacturer Manual | Puhui T-962A specifications, 8 thermal waves, safety & maintenance |
| 10 | `NXP_AN10365_Surface_Mount_Reflow_Soldering.pdf` | `NXP-AN10365-REV8` | 31 | 45 | 183 | Application Note | Lead-free & SnPb reflow soldering, MSL handling, board attachment & rework |
| 11 | `TI_SLUA271C_QFN_SON_PCB_Attachment_Guidelines.pdf` | `TI-SLUA271C` | 21 | 10 | 105 | Application Note | QFN/SON land patterns, stencil aperture ratios, X-ray void inspection |
| 12 | `TI_SLOA122_QFN_Layout_And_Assembly_Guidelines.pdf` | `TI-SLOA122` | 7 | 1 | 21 | Application Note | QFN thermal pad vias, solder mask design, segmented stencil opening |
| 13 | `TI_SPRAA99_BGA_SMT_Guidelines.pdf` | `TI-SPRAA99` | 62 | 29 | 197 | Application Note | nFBGA SMT placement, convection reflow profiles, inspection & reliability |
| 14 | `Research_Paper_SMT_Inspection_DVQI_2312.09232.pdf` | `ARXIV-2312-09232` | 8 | 1 | 44 | Scientific Paper | DVQI inline automated visual inspection architecture (`arXiv:2312.09232`) |
| 15 | `Research_Paper_SPI_PCB_Defect_Detection_2309.03113.pdf` | `ARXIV-2309-03113` | 6 | 2 | 35 | Scientific Paper | ML defect detection on 3D SPI pin features (`arXiv:2309.03113`) |

---

## 2. Source Details

### External Manufacturer & Academic References
* **`T962A_Infrared_Reflow_Oven_Official_Manual.pdf`**: Official user manual published by Puhui Technology for the T-962A Desktop Infrared IC Heater. Used to validate extraction on multi-page real-world equipment manuals.
* **`NXP_AN10365_Surface_Mount_Reflow_Soldering.pdf`**: Official NXP Semiconductors Application Note *Surface mount reflow soldering* (Rev. 8, October 2021) — [`https://www.nxp.com/docs/en/application-note/AN10365.pdf`](https://www.nxp.com/docs/en/application-note/AN10365.pdf).
* **`TI_SLUA271C_QFN_SON_PCB_Attachment_Guidelines.pdf`**: Official Texas Instruments Application Note *QFN and SON PCB Attachment* (`SLUA271C`) — [`https://www.ti.com/lit/pdf/slua271`](https://www.ti.com/lit/pdf/slua271).
* **`TI_SLOA122_QFN_Layout_And_Assembly_Guidelines.pdf`**: Official Texas Instruments Application Report *QFN Layout Guidelines* (`SLOA122`) — [`https://www.ti.com/lit/pdf/sloa122`](https://www.ti.com/lit/pdf/sloa122).
* **`TI_SPRAA99_BGA_SMT_Guidelines.pdf`**: Official Texas Instruments Application Report *nFBGA Packaging* (`SPRAA99`) — [`https://www.ti.com/lit/pdf/spraa99`](https://www.ti.com/lit/pdf/spraa99).
* **`Research_Paper_SMT_Inspection_DVQI_2312.09232.pdf`**: Open-access preprint from Cornell University arXiv (`arXiv:2312.09232 [cs.CV]`, Dec 2023) — [`https://arxiv.org/pdf/2312.09232`](https://arxiv.org/pdf/2312.09232).
* **`Research_Paper_SPI_PCB_Defect_Detection_2309.03113.pdf`**: Open-access preprint from Cornell University arXiv (`arXiv:2309.03113`, Sep 2023) — [`https://arxiv.org/pdf/2309.03113`](https://arxiv.org/pdf/2309.03113).

### Standardized Factory SOP Documents
* Generated reproducibly using ReportLab via [`data/generate_sample_sops.py`](../generate_sample_sops.py) (`001`–`003`) and [`backend/scripts/generate_additional_sops.py`](../../backend/scripts/generate_additional_sops.py) (`004`–`008`).
* Structured around **IPC-A-610 Class 3**, **IPC-A-600J**, **IPC-7525B**, **IPC-7527**, **ANSI/ESD S20.20-2021**, and **IPC/JEDEC J-STD-033D** electronics assembly standards.

---

## 3. PDF Ingestion Characteristics

The corpus exercises key real-world edge cases for `pdf_parser.py` and `chunker.py`:
1. **Multi-Page Tables:** `SOP_SMT_001` and `SOP_REFLOW_002` split error-code/defect tables across pages without repeating headers on page 2, testing header inheritance.
2. **Dense Manufacturer Tables:** `NXP_AN10365` (45 tables) and `TI_SPRAA99` (29 tables) stress Markdown table serialization, multi-line header formatting, and Table-Aware row chunking.
3. **Multi-Line Table Cells & Domain Tokens:** Alarm codes (`E-101`, `E-204`, `SP-203`, `ESD-01`, `SPI-302`) and numeric tolerances (`>1.2 Nm`, `<= 0.025 mm`, `0.75-35 MOhm`) test token preservation and dual retrieval.
4. **Mixed Document Layouts:** Multi-column IEEE-style academic papers (`arXiv:2312.09232`, `arXiv:2309.03113`), 62-page engineering datasheets (`TI_SPRAA99`), and structured shop-floor SOPs validate section tracking across heterogeneous formatting.
