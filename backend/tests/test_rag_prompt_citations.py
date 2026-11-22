"""
Unit test suite cho Milestone 3.1 - Phần 2 (Prompt Guardrails & Citation Verification):
- Định dạng ngữ cảnh có giới hạn độ dài max_chars và ghép Hard Guardrails Prompt
- Đối soát trích dẫn [Tên file - Trang X] khớp 100% chunk thực tế
- Loại bỏ trích dẫn bịa số trang / sai tên file (Anti-Hallucination)
- Trả về citations == [] khi câu trả lời là từ chối chuẩn
"""
from app.rag.citations import extract_verified_citations, strip_unverified_citations
from app.rag.prompt_engine import (
    REFUSAL_MESSAGE,
    SYSTEM_PROMPT,
    build_rag_prompt,
    format_context_blocks,
)


def _sample_chunks():
    return [
        {
            "chroma_id": "doc-feeder:1:3",
            "score": 0.92,
            "content": "| E-204 | Carrier cover film broke | 1. Press Yellow Pause button. 2. Clear sheared cover tape. | High |",
            "metadata": {
                "doc_id": "doc-feeder",
                "doc_code": "SOP-FEEDER-004-VN",
                "source_file": "SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf",
                "page_num": 1,
                "chunk_index": 3,
                "section_title": "3. FEEDER TROUBLESHOOTING & ALARM CODES TABLE - Bảng tra cứu",
                "is_table": True,
            },
        },
        {
            "chroma_id": "doc-smt:2:4",
            "score": 0.78,
            "content": "Clean downward-looking camera optical lens with micro-fiber cloth.",
            "metadata": {
                "doc_id": "doc-smt",
                "doc_code": "SOP-SMT-001-VN",
                "source_file": "SOP_SMT_001_Pick_And_Place_Machine_Troubleshooting.pdf",
                "page_num": 2,
                "chunk_index": 4,
                "section_title": "3. SYSTEM ERROR CODE MATRIX",
                "is_table": False,
            },
        },
    ]


def test_format_context_blocks_and_build_rag_prompt():
    """Định dạng khối ngữ cảnh kèm metadata và ghép prompt tuân thủ giới hạn max_chars."""
    chunks = _sample_chunks()
    ctx = format_context_blocks(chunks, max_chars=280)
    assert "SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf" in ctx
    assert "Trang: 1" in ctx
    # Chunk thứ 2 vượt quá max_chars=280 nên không được gộp thêm
    assert "SOP_SMT_001_Pick_And_Place_Machine_Troubleshooting.pdf" not in ctx

    prompt_pack = build_rag_prompt("Máy báo lỗi E-204 xử lý sao?", chunks)
    assert REFUSAL_MESSAGE in prompt_pack["system_prompt"]
    assert prompt_pack["system_prompt"] == SYSTEM_PROMPT
    assert "[NGỮ CẢNH TÀI LIỆU]" in prompt_pack["user_prompt"]
    assert "Máy báo lỗi E-204 xử lý sao?" in prompt_pack["user_prompt"]


def test_extract_verified_citations_valid_match():
    """Đối soát thành công các thẻ trích dẫn hợp lệ (kể cả viết không có .pdf hoặc lặp nhiều lần)."""
    chunks = _sample_chunks()
    answer = (
        "📌 Lỗi E-204 kẹt cuộn feeder.\n"
        "🛠️ Bước xử lý: Nhấn nút Pause và gỡ màng băng bị đứt "
        "[SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf - Trang 1].\n"
        "📖 Nguồn: [SOP_FEEDER_004_Tape_And_Reel_Setup_Guide - Page 1]"
    )

    citations = extract_verified_citations(answer, chunks)
    assert len(citations) == 1
    c = citations[0]
    assert c["doc_id"] == "doc-feeder"
    assert c["file"] == "SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf"
    assert c["page"] == 1
    assert c["score"] == 0.92
    assert "E-204" in c["snippet"]


def test_extract_verified_citations_rejects_hallucinated_page_or_file():
    """Loại bỏ triệt để trích dẫn bịa số trang (Trang 99) hoặc bịa tên file không có trong chunk."""
    chunks = _sample_chunks()
    answer = (
        "Thực hiện theo [SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf - Trang 1], "
        "ngoài ra tham khảo [SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf - Trang 99] "
        "và [Fake_Manual_2027.pdf - Trang 3]."
    )

    citations = extract_verified_citations(answer, chunks, fallback_to_retrieved=False)
    assert len(citations) == 1
    assert citations[0]["file"] == "SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf"
    assert citations[0]["page"] == 1


def test_extract_verified_citations_empty_on_refusal():
    """Nếu LLM trả về mẫu từ chối chuẩn hoặc không có chunk truy hồi, citations phải rỗng."""
    chunks = _sample_chunks()
    assert extract_verified_citations(REFUSAL_MESSAGE, chunks) == []
    assert extract_verified_citations("Trả lời bình thường [SOP_SMT_001 - Trang 2]", []) == []


def test_strip_unverified_citations():
    """strip_unverified_citations giữ nguyên thẻ trích dẫn thật và gỡ sạch thẻ bịa đặt."""
    chunks = _sample_chunks()
    raw_answer = (
        "Xử lý theo hướng dẫn [SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf - Trang 1] "
        "hoặc xem thêm [Hallucinated_Doc.pdf - Trang 5]."
    )

    cleaned = strip_unverified_citations(raw_answer, chunks)
    assert "[SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf - Trang 1]" in cleaned
    assert "Hallucinated_Doc.pdf" not in cleaned
    assert "Trang 5" not in cleaned
