# Dataset Provenance & Technical Overview

This file documents the origin, structure, and ingestion test characteristics of the 7 PDF documents in `data/sops/`.

---

## 1. Document Inventory

| # | File Name | Document Code | Pages | Category | Key Technical Focus |
| :---: | :--- | :---: | :---: | :--- | :--- |
| 1 | `SOP_SMT_001_Pick_And_Place_Machine_Troubleshooting.pdf` | `SOP-SMT-FUJI-001` | 2 | Standardized SOP | Pick-and-place error matrix (`E-101`, `E-104`, `E-112`, `E-205`), preventive maintenance |
| 2 | `SOP_REFLOW_002_Reflow_Soldering_Defects_Remedies.pdf` | `SOP-REFLOW-002` | 2 | Standardized SOP | Reflow thermal profiles, Tombstoning, Solder Balling, Bridging, BGA Voiding |
| 3 | `SOP_AOI_003_Automated_Optical_Inspection_Standards.pdf` | `SOP-AOI-003` | 1 | Standardized SOP | Post-reflow 3D AOI criteria (IPC-A-610 Class 3) & escalation protocol |
| 4 | `SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf` | `SOP-FEEDER-004-VN` | 2 | Standardized SOP | Feeder reel loading, calibration, alarm codes (`E-204`, `E-201`, `E-208`) |
| 5 | `SOP_PCB_005_Bare_Board_Cleanliness_And_Inspection.pdf` | `SOP-PCB-005-VN` | 1 | Standardized SOP | Bare PCB defect matrix (`PCB-D01`–`PCB-D03`), moisture sensitivity & baking |
| 6 | `T962A_Infrared_Reflow_Oven_Official_Manual.pdf` | `MANUAL-PUHUI-T962A` | 8 | Manufacturer Manual | Puhui T-962A specifications, 8 thermal waves, safety & maintenance |
| 7 | `Research_Paper_SMT_Inspection_DVQI_2312.09232.pdf` | `ARXIV-2312-09232` | 8 | Scientific Paper | DVQI inline automated visual inspection architecture (arXiv:2312.09232) |

---

## 2. Source Details

### External Manufacturer & Academic References
* **`T962A_Infrared_Reflow_Oven_Official_Manual.pdf`**: Official user manual published by Puhui Technology for the T-962A Desktop Infrared IC Heater. Used to validate extraction on multi-page real-world equipment manuals.
* **`Research_Paper_SMT_Inspection_DVQI_2312.09232.pdf`**: Open-access preprint from Cornell University arXiv (`arXiv:2312.09232 [cs.CV]`, Dec 2023) by Chung et al. Used to validate multi-column technical paper extraction.

### Standardized Factory SOP Documents
* Generated reproducibly using ReportLab via [`data/generate_sample_sops.py`](../generate_sample_sops.py) and [`backend/scripts/generate_additional_sops.py`](../../backend/scripts/generate_additional_sops.py).
* Structured around **IPC-A-610 Class 3**, **IPC-A-600J**, and **IPC/JEDEC J-STD-033D** electronics assembly standards.

---

## 3. PDF Ingestion Characteristics

The dataset exercises key edge cases for `pdf_parser.py` and `chunker.py`:
1. **Multi-Page Tables:** `SOP_SMT_001` splits an error-code table across pages 1 and 2 without repeating headers on page 2, testing header inheritance.
2. **Multi-Line Table Cells:** Error descriptions and numbered corrective steps contain embedded newlines (`\n`) and special tokens like `E-204` or `>1.2 Nm`, testing Markdown escaping and row integrity.
3. **Mixed Font Hierarchies:** Different heading font sizes (`13pt`, `18pt`) alongside multi-column research paper layouts test heading detection and prose splitting.
