# SmartSOP AI — System Architecture & Design

This document describes the current backend architecture, relational database schema, role-based access control (RBAC) matrix, incident lifecycle rules, and document ingestion pipeline for SmartSOP AI.

---

## 1. High-Level System Architecture

```mermaid
flowchart LR
    Client["Web Client / Swagger UI<br/>(Bearer JWT + SSE)"] --> API["FastAPI REST & SSE Gateway<br/>(/api/v1)"]

    subgraph Core["Backend Core (Implemented)"]
        Auth["Auth & RBAC Dependencies<br/>PyJWT + Bcrypt + require_roles"]
        CRUD["Domain Routers<br/>Lines, Machines, Users, SOPs, Tickets"]
        Parser["PDF Parser & Chunker<br/>pdfplumber + Table-Aware Chunker"]
        DB[("SQLite / PostgreSQL<br/>7 Async ORM Tables")]
        FS[("Local File Storage<br/>SHA-256 Deduplicated PDFs")]
    end

    subgraph RAG["RAG Engine (Next Phase)"]
        Embed["BAAI/bge-m3<br/>Multilingual Embeddings"]
        Vector[("ChromaDB<br/>Cosine Vector Store")]
        LLM["LLM Provider<br/>Gemini API / Ollama Local"]
    end

    API --> Auth --> CRUD
    CRUD --> DB
    CRUD --> FS
    CRUD --> Parser
    Parser -.-> Embed -.-> Vector
    API -.-> Vector -.-> LLM
```

---

## 2. Relational Database Schema (7 Tables)

All tables use string UUID primary keys (`String(36)`) and UTC timestamp tracking (`created_at`, `updated_at`) via SQLAlchemy 2.0 async models.

```mermaid
erDiagram
    users ||--o{ sop_documents : "uploads"
    users ||--o{ incident_tickets : "reports"
    users ||--o{ chat_audit_logs : "queries"
    production_lines ||--o{ machines : "contains"
    production_lines ||--o{ sop_documents : "applies_to"
    machines ||--o{ sop_documents : "documents"
    machines ||--o{ incident_tickets : "experiences"
    sop_documents ||--o{ sop_chunks : "splits_into"
    sop_documents ||--o{ incident_tickets : "suggested_for"

    users {
        string id PK
        string username UK
        string password_hash
        string full_name
        string email UK
        enum role
        boolean is_active
    }

    production_lines {
        string id PK
        string name UK
        string factory_zone
        string description
    }

    machines {
        string id PK
        string line_id FK
        string machine_code UK
        string name
        string model
        string manufacturer
        enum status
    }

    sop_documents {
        string id PK
        string document_code UK
        string title
        string file_name
        string file_path
        string file_hash
        int file_size
        string version
        int page_count
        int chunk_count
        enum ingestion_status
        string line_id FK
        string machine_id FK
        string uploaded_by FK
    }

    sop_chunks {
        string id PK
        string document_id FK
        string chroma_id UK
        int page_num
        int chunk_index
        string section_title
        int char_count
        boolean is_table
    }

    incident_tickets {
        string id PK
        string ticket_code UK
        string machine_id FK
        string reported_by FK
        string error_code
        string description
        enum priority
        enum status
        string suggested_sop_id FK
        int suggested_page
        datetime started_at
        datetime resolved_at
    }

    chat_audit_logs {
        string id PK
        string user_id FK
        string question
        text answer
        string cited_doc_ids
        string cited_pages
        float top_score
        boolean is_refused
        int ttft_ms
        int latency_ms
    }
```

> **Retention Design:** Deleting a `User` preserves factory incident history and chat logs via `ondelete="SET NULL"` rather than cascading deletes.

---

## 3. Role-Based Access Control (RBAC) Matrix

Access control is enforced at the FastAPI router/endpoint level via `require_roles([...])`:

| Resource / Action | `OPERATOR` | `SHIFT_ENGINEER` | `FACTORY_MANAGER` | `ADMIN` |
| :--- | :---: | :---: | :---: | :---: |
| Login & View Own Profile | Yes | Yes | Yes | Yes |
| View Lines, Machines, Tickets & SOP List | Yes | Yes | Yes | Yes |
| Stream Authenticated PDF (`/sop_documents/{id}/file`) | Yes | Yes | Yes | Yes |
| Create & Update Incident Tickets | No (`403`) | Yes | Yes | Yes |
| Create / Update Production Lines & Machines | No (`403`) | Yes | Yes | Yes |
| Upload & Update SOP Metadata | No (`403`) | No (`403`) | Yes | Yes |
| Delete Lines, Machines, Tickets, SOPs | No (`403`) | No (`403`) | No (`403`) | Yes |
| Manage Users (`/users` CRUD) | No (`403`) | No (`403`) | No (`403`) | Yes |

---

## 4. Incident Ticket State Machine

To ensure accurate Mean Time To Repair (MTTR) metrics (`resolved_at - started_at`), `PATCH /api/v1/incident_tickets/{id}` enforces strict status transitions:

```mermaid
stateDiagram-v2
    [*] --> OPEN
    OPEN --> IN_PROGRESS : Sets started_at
    OPEN --> CLOSED : Cancelled without repair
    IN_PROGRESS --> RESOLVED : Sets resolved_at
    IN_PROGRESS --> OPEN : Reassigned
    RESOLVED --> CLOSED : Verified & closed
    RESOLVED --> IN_PROGRESS : Reopened
    CLOSED --> IN_PROGRESS : Reopened
```

Direct jumps from `OPEN` to `RESOLVED` are rejected with `HTTP 400 Bad Request`.

---

## 5. Table-Aware PDF Ingestion Pipeline

Industrial SOPs frequently embed alarm code matrices inside multi-page PDF tables. Standard fixed-size character splitting breaks rows and separates error codes from column headers. SmartSOP AI prevents this with a two-stage pipeline:

1. **Extraction (`backend/app/utils/pdf_parser.py`):**
   * Extracts per-page text and tables using `pdfplumber`.
   * Formats each table as standard Markdown (`| Col 1 | Col 2 |`) and detects continuation tables across page boundaries (inheriting headers when a page starts directly with an error-code row).
   * Identifies structural headings (`H1`/`H2`/`H3`) using font size and numbering patterns.
2. **Table-Aware Chunking (`backend/app/utils/chunker.py`):**
   * Prose sections are split via `RecursiveCharacterTextSplitter` (`chunk_size=800`, `chunk_overlap=150`, heading-first separators).
   * Short tables (`<= 2000` chars) stay intact in a single chunk (`is_table=True`).
   * Long tables are grouped by complete rows, repeating the Markdown header and separator line at the top of every chunk.
