# SmartSOP AI — Industrial SOP Management & RAG Assistant

SmartSOP AI is an async FastAPI + RAG platform designed for electronics manufacturing and SMT (Surface-Mount Technology) assembly lines. It centralizes factory Standard Operating Procedures (SOPs), enforces role-based equipment and incident ticket workflows, and parses complex multi-page PDF manuals into table-aware chunks for grounded troubleshooting assistance.

* Architecture & Database Schema: [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)
* Sample Industrial Dataset: [data/sops/README.md](./data/sops/README.md)
* Interactive UI Prototypes: [docs/ui-prototypes/index.html](./docs/ui-prototypes/index.html)

---

## Key Features

1. **SOP Document Management & Secure File Streaming:**
   * PDF upload with automatic SHA-256 checksum calculation to block duplicate files.
   * Authenticated binary PDF streaming (`GET /api/v1/sop_documents/{id}/file`) protected by Bearer JWT tokens.
2. **Table-Aware PDF Ingestion Pipeline (`pdfplumber` + `langchain-text-splitters`):**
   * Extracts error-code and defect matrices into structured Markdown tables (`| ... |`) with cross-page table header inheritance.
   * Detects H1/H2/H3 section headings via font size and numbering patterns.
   * Splits long tables by row groups while repeating column headers in every chunk so error codes and corrective steps never lose context.
3. **Incident Ticket Lifecycle Management:**
   * Tracks factory equipment incidents linked to production lines, machines, and error codes.
   * Enforces strict state-machine transitions (`OPEN` -> `IN_PROGRESS` -> `RESOLVED` -> `CLOSED`, rejecting direct `OPEN` -> `RESOLVED` jumps) with automatic `started_at` and `resolved_at` timestamps for MTTR calculation.
4. **JWT Authentication & 4-Role RBAC Middleware:**
   * Role-based permissions enforced via FastAPI dependencies across `ADMIN`, `FACTORY_MANAGER`, `SHIFT_ENGINEER`, and `OPERATOR`.
   * Bcrypt password hashing, 8-hour shift-aligned JWT tokens, and automatic self-deletion prevention for admins.
5. **Planned RAG Query Engine & React Operations Console:**
   * Multilingual `BAAI/bge-m3` embeddings + ChromaDB vector store, dual error-code + semantic retrieval, anti-hallucination prompt guardrails with page citations, SSE streaming, and a React 18 + Tailwind CSS dashboard.

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Backend API** | Python 3.12, FastAPI, Uvicorn, Pydantic v2 |
| **Database & ORM** | SQLAlchemy 2.0 (Async), `asyncpg` (PostgreSQL) / `aiosqlite` (Local Dev), Alembic |
| **Auth & Security** | PyJWT (HS256), Passlib + Bcrypt, 4-Role RBAC dependencies |
| **PDF & Chunking** | `pdfplumber`, `pypdf`, `langchain-text-splitters`, ReportLab |
| **Vector & LLM (Planned)** | `BAAI/bge-m3`, ChromaDB, Google Gemini API / Ollama Local |
| **Frontend (Prototype Ready)** | React 18, Vite, Tailwind CSS, Lucide Icons, Recharts |
| **Testing** | Pytest, `pytest-asyncio`, HTTPX `ASGITransport` |

---

## Repository Structure

```text
.
├── backend/
│   ├── alembic/                  # Async SQLAlchemy database migrations
│   ├── app/
│   │   ├── core/                 # Settings, async DB engine, JWT security, RBAC dependencies
│   │   ├── models/               # 7 SQLAlchemy ORM models (users, lines, machines, SOPs, chunks, tickets, logs)
│   │   ├── routers/              # REST endpoints (auth, users, production_lines, machines, sop_documents, incident_tickets)
│   │   ├── schemas/              # Pydantic v2 request/response models
│   │   ├── utils/                # pdf_parser.py & chunker.py (table-aware PDF ingestion)
│   │   └── main.py               # FastAPI application entrypoint
│   ├── scripts/
│   │   ├── seed_data.py          # Idempotent seed script (4 roles, 2 SMT lines, 5 machines, 3 SOPs)
│   │   └── generate_additional_sops.py
│   ├── tests/                    # Automated test suite (41/41 passing)
│   ├── .env.example
│   └── requirements.txt
├── data/
│   ├── generate_sample_sops.py   # Sample industrial SOP PDF generator
│   └── sops/                     # Sample SMT manuals & SOP PDFs + provenance metadata
└── docs/
    ├── ARCHITECTURE.md           # System architecture, ERD, RBAC matrix, and ticket state machine
    └── ui-prototypes/            # Interactive 6-screen Dark Industrial HTML prototype
```

---

## Engineering Roadmap

| Phase | Milestone | Focus Area | Status |
| :---: | :--- | :--- | :---: |
| **Phase 1** | **M1.1** | Project setup, 7-table async ORM schema, Alembic migrations, idempotent seed script | **Done** |
| | **M1.2** | JWT authentication, Bcrypt password hashing, profile & token validation tests | **Done** |
| | **M1.3** | RBAC dependencies, CRUD APIs (Lines, Machines, Users, Tickets, SOPs + SHA-256 upload) | **Done** |
| **Phase 2** | **M2.1** | `pdfplumber` Markdown table extraction, heading detection, table-aware chunking (41/41 tests) | **Done** |
| | **M2.2** | `BAAI/bge-m3` embeddings, ChromaDB vector store, background ingestion worker | **Next** |
| **Phase 3** | **M3.x** | Dual-retrieval (error-code regex + cosine search), guardrails, citations, SSE chat API | *Planned* |
| **Phase 4** | **M4.x** | React 18 + Vite frontend (SSE streaming UI, PDF citation viewer, KPI dashboard) | *Planned* |
| **Phase 5** | **M5.x** | RAG quality benchmarks, evaluation suite, and multi-container Docker Compose setup | *Planned* |

---

## Getting Started

### Prerequisites
* Python 3.11+
* Git

### Backend Setup & Run
```powershell
# 1. Create and activate virtual environment (from project root)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install backend dependencies
cd backend
pip install -r requirements.txt

# 3. Configure environment variables
copy .env.example .env

# 4. Run database migrations and load initial seed data
alembic upgrade head
python scripts/seed_data.py

# 5. Start the development server
uvicorn app.main:app --reload --port 8000
```

Interactive API documentation is available once the server is running:
* Swagger UI: `http://localhost:8000/docs`
* ReDoc: `http://localhost:8000/redoc`

### Running Tests
```powershell
cd backend
pytest -v
```
