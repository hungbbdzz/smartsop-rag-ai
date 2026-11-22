# Industrial SOP & Technical Manual Dataset

This directory contains sample SMT (Surface-Mount Technology) manufacturing manuals, technical inspection papers, and standardized operating procedures used for developing and testing SmartSOP AI's PDF ingestion and RAG pipeline.

---

## 1. Public Manufacturer & Research References

1. **[`T962A_Infrared_Reflow_Oven_Official_Manual.pdf`](./T962A_Infrared_Reflow_Oven_Official_Manual.pdf)** *(8 pages)*
   * **Source:** Puhui Technology T-962A Desktop Infrared IC Heater Official User Manual.
   * **Content:** Hardware specs (1500W, 300 x 320 mm soldering area), 8 thermal wave profiles (Wave 1–8), operating steps, and maintenance instructions.
2. **[`Research_Paper_SMT_Inspection_DVQI_2312.09232.pdf`](./Research_Paper_SMT_Inspection_DVQI_2312.09232.pdf)** *(8 pages)*
   * **Source:** arXiv preprint `2312.09232 [cs.CV]` — *"DVQI: A Multi-task, Hardware-integrated Artificial Intelligence System for Automated Visual Inspection in Electronics Manufacturing"*.
   * **Content:** Computer vision defect classification and inline SMT automated visual inspection benchmarks.

---

## 2. Standardized SMT Factory SOPs

Five structured SOP PDFs modeled on IPC-A-610, IPC-A-600J, and IPC/JEDEC J-STD-033D workflows, featuring alarm/defect tables and step-by-step corrective actions:

1. **[`SOP_SMT_001_Pick_And_Place_Machine_Troubleshooting.pdf`](./SOP_SMT_001_Pick_And_Place_Machine_Troubleshooting.pdf)** (`SOP-SMT-FUJI-001`, 2 pages)
   * High-speed SMT pick-and-place troubleshooting (`E-101` Feeder Jam, `E-104` Nozzle Vacuum Drop, `E-112` Fiducial Recognition Failed, `E-205` Component Pick Offset), with a cross-page error table.
2. **[`SOP_REFLOW_002_Reflow_Soldering_Defects_Remedies.pdf`](./SOP_REFLOW_002_Reflow_Soldering_Defects_Remedies.pdf)** (`SOP-REFLOW-002`, 2 pages)
   * Reflow thermal profile requirements and remedies for Tombstoning, Solder Balling, Solder Bridging, and BGA/QFN Voiding.
3. **[`SOP_AOI_003_Automated_Optical_Inspection_Standards.pdf`](./SOP_AOI_003_Automated_Optical_Inspection_Standards.pdf)** (`SOP-AOI-003`, 1 page)
   * Post-reflow 3D AOI inspection criteria (IPC-A-610 Class 3) and line-stop escalation rules.
4. **[`SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf`](./SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf)** (`SOP-FEEDER-004-VN`, 2 pages)
   * Electric tape feeder setup, preventive maintenance, and troubleshooting matrix (`E-204` Feeder Jam / Pickup Reject, `E-201` Feeder ID Comm Error, `E-208` Component Pitch Offset).
5. **[`SOP_PCB_005_Bare_Board_Cleanliness_And_Inspection.pdf`](./SOP_PCB_005_Bare_Board_Cleanliness_And_Inspection.pdf)** (`SOP-PCB-005-VN`, 1 page)
   * Incoming bare PCB cleanliness and inspection matrix (`PCB-D01` Pad Oxidation, `PCB-D02` Substrate Warpage, `PCB-D03` Fiducial Scratch) and baking profiles.

See [PROVENANCE.md](./PROVENANCE.md) for full provenance and ingestion testing notes.
