"""
Unit test suite for Milestone 2.1 (Gate Test 2.1):
- Bóc tách PDF Kỹ thuật & Bảng mã lỗi Markdown (pdf_parser.py)
- Chiến lược phân đoạn ngữ nghĩa Table-Aware Chunking (chunker.py)
"""
from pathlib import Path
import pytest

from app.core.config import settings
from app.utils.pdf_parser import (
    extract_text_by_page,
    extract_tables_as_markdown,
    detect_headings,
    parse_pdf_document,
)
from app.utils.chunker import chunk_document, TableAwareChunker


SOPS_DIR = Path(settings.PROJECT_ROOT) / "data" / "sops"
if not SOPS_DIR.exists():
    SOPS_DIR = Path(settings.BACKEND_DIR) / "data" / "sops"


def test_gate_test_2_1_all_pdf_pages_non_empty():
    """GATE TEST 2.1: extract_text_by_page đọc thành công tất cả file PDF mẫu, không trang nào bị rỗng."""
    pdf_files = list(SOPS_DIR.glob("*.pdf"))
    assert len(pdf_files) >= 6, f"Cần ít nhất 6 file PDF kỹ thuật trong {SOPS_DIR}, hiện có: {len(pdf_files)}"

    for pdf_path in pdf_files:
        pages = extract_text_by_page(pdf_path)
        assert len(pages) > 0, f"File {pdf_path.name} không trích xuất được trang nào"
        for p in pages:
            # Mỗi trang phải có nội dung văn bản (không bị rỗng)
            assert len(p["text"].strip()) > 0, f"Trang {p['page_number']} của {pdf_path.name} bị rỗng!"
            assert p["char_count"] > 20, f"Trang {p['page_number']} của {pdf_path.name} có quá ít ký tự"


def test_gate_test_2_1_error_code_e204_in_markdown_table():
    """GATE TEST 2.1: Bảng mã lỗi E-204 của máy gắp linh kiện xuất hiện nguyên vẹn định dạng bảng Markdown (chứa ký tự |)."""
    target_pdf = SOPS_DIR / "SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf"
    assert target_pdf.exists(), f"Không tìm thấy file {target_pdf.name}"

    tables = extract_tables_as_markdown(target_pdf)
    assert len(tables) >= 1, "Phải trích xuất được ít nhất 1 bảng biểu từ file Feeder SOP"

    found_e204 = False
    for t in tables:
        md = t["markdown"]
        if "E-204" in md:
            found_e204 = True
            # Kiểm tra định dạng bảng Markdown chuẩn
            assert "|" in md, "Bảng mã lỗi phải chứa ký tự phân cách |"
            assert "| --- |" in md or "---" in md, "Bảng Markdown phải có dòng kẻ phân cách tiêu đề (---)"
            assert "Error Code" in md, "Bảng phải có tiêu đề cột Error Code"
            assert "Feeder Jam" in md, "Mô tả lỗi E-204 phải có Feeder Jam"
            break

    assert found_e204 is True, "Không tìm thấy mã lỗi E-204 trong bảng biểu Markdown nào!"


def test_gate_test_2_1_table_chunks_contain_headers_and_row_integrity():
    """
    GATE TEST 2.1:
    - Mọi chunk sinh ra từ bảng biểu đều chứa tiêu đề cột rõ ràng.
    - Không có bất kỳ chunk nào bị cắt xẻ đôi giữa một dòng mã lỗi.
    """
    target_pdf = SOPS_DIR / "SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf"
    parsed_doc = parse_pdf_document(target_pdf)
    chunks = chunk_document(parsed_doc)

    table_chunks = [c for c in chunks if c["is_table"]]
    assert len(table_chunks) >= 1, "Phải có ít nhất 1 chunk thuộc loại bảng biểu"

    for tc in table_chunks:
        content = tc["content"]
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        
        # 1. Mọi chunk bảng đều phải có dòng tiêu đề cột
        assert "|" in lines[0], f"Dòng đầu tiên của chunk bảng phải là header: {lines[0]}"
        assert "Error Code" in lines[0] or "Mã lỗi" in lines[0] or "Cột" in lines[0]

        # 2. Dòng thứ 2 phải là dòng kẻ markdown (---)
        assert "---" in lines[1], f"Dòng thứ hai phải là dòng kẻ phân cách: {lines[1]}"

        # 3. Tính toàn vẹn của các hàng dữ liệu: Số lượng cột trong mỗi hàng phải khớp với header
        num_header_cols = lines[0].count("|") - 1
        for row_line in lines[2:]:
            num_row_cols = row_line.count("|") - 1
            assert num_row_cols == num_header_cols, (
                f"Hàng dữ liệu bị cắt đôi hoặc lệch cột: {row_line} (kỳ vọng {num_header_cols} cột, có {num_row_cols})"
            )


def test_table_aware_chunker_long_table_repeats_headers():
    """Kiểm tra chiến lược Table-Aware: Bảng dài khi bị chia nhỏ thì MỌI CHUNK đều được lặp lại Header."""
    chunker = TableAwareChunker(max_table_chunk_size=300, rows_per_table_chunk=2)

    sample_md_table = """
| Mã lỗi | Tên sự cố | Giải pháp khắc phục |
| --- | --- | --- |
| E-01 | Quá nhiệt buồng 1 | Hạ nhiệt độ xuống 5 độ |
| E-02 | Quá nhiệt buồng 2 | Kiểm tra quạt gió đối lưu |
| E-03 | Lệch áp suất khí | Tăng áp suất bình khí nén |
| E-04 | Kẹt băng chuyền | Vệ sinh con lăn và tra dầu |
| E-05 | Lỗi cảm biến quang | Lau mắt kính cảm biến |
""".strip()

    sub_chunks = chunker.split_table_to_chunks(
        markdown_table=sample_md_table,
        page_number=1,
        section_title="Bảng thử nghiệm",
        raw_headers=["Mã lỗi", "Tên sự cố", "Giải pháp khắc phục"],
    )

    # 5 dòng dữ liệu chia mỗi chunk 2 dòng -> Cần 3 chunks
    assert len(sub_chunks) == 3
    for idx, c in enumerate(sub_chunks):
        content = c["content"]
        assert c["is_table"] is True
        # Mọi chunk đều phải lặp lại tiêu đề
        assert "| Mã lỗi | Tên sự cố | Giải pháp khắc phục |" in content, (
            f"Chunk {idx+1} không lặp lại dòng tiêu đề cột!"
        )
        assert "| --- | --- | --- |" in content


def test_detect_headings_functionality():
    """Kiểm tra tính năng phát hiện tiêu đề dựa trên font size và mẫu số thứ tự mục."""
    target_pdf = SOPS_DIR / "SOP_SMT_001_Pick_And_Place_Machine_Troubleshooting.pdf"
    headings = detect_headings(target_pdf)
    assert len(headings) > 0

    heading_texts = [h["text"] for h in headings]
    # Phải bắt được các mục lớn như PURPOSE, ERROR CODE MATRIX, MAINTENANCE...
    assert any("PURPOSE" in t for t in heading_texts)
    assert any("ERROR CODE" in t or "PROCEDURES" in t for t in heading_texts)
    assert any("MAINTENANCE" in t for t in heading_texts)


def test_parse_pdf_document_full_metadata():
    """Kiểm tra hàm parse_pdf_document trích xuất đầy đủ metadata và bóc tách hoàn chỉnh."""
    target_pdf = SOPS_DIR / "SOP_PCB_005_Bare_Board_Cleanliness_And_Inspection.pdf"
    doc = parse_pdf_document(target_pdf)

    assert doc["file_name"] == "SOP_PCB_005_Bare_Board_Cleanliness_And_Inspection.pdf"
    assert len(doc["file_hash"]) == 64  # SHA-256
    assert doc["file_size"] > 0
    assert doc["total_pages"] == 1
    assert doc["total_tables"] >= 1
    assert len(doc["pages"]) == 1
    assert doc["pages"][0]["has_tables"] is True


def test_reflow_002_page2_continuation_table_inherits_headers():
    """Bảng nối tiếp ở trang 2 SOP_REFLOW_002 phải kế thừa Header từ trang 1, giữ nguyên dòng Voiding in BGA/QFN."""
    target_pdf = SOPS_DIR / "SOP_REFLOW_002_Reflow_Soldering_Defects_Remedies.pdf"
    parsed_doc = parse_pdf_document(target_pdf)
    chunks = chunk_document(parsed_doc)

    page2_tables = [c for c in chunks if c["is_table"] and c["page_number"] == 2]
    assert len(page2_tables) == 1
    tc = page2_tables[0]

    assert tc["table_headers"] == [
        "Defect Name",
        "Physical Mechanism & Root Cause",
        "Corrective Remediation Protocol",
    ]
    lines = [line.strip() for line in tc["content"].split("\n") if line.strip()]
    assert "Defect Name" in lines[0]
    assert any(
        "Voiding in BGA/QFN" in row.replace("<br/>", " ") for row in lines[2:]
    ), "Dòng 'Voiding in BGA/QFN' bị biến thành Header thay vì dữ liệu!"
    # Trang 2 của SOP_REFLOW_002 chỉ có bảng nối tiếp -> không sinh prose chunk trùng lặp
    page2_prose = [c for c in chunks if not c["is_table"] and c["page_number"] == 2]
    assert page2_prose == []


def test_no_duplicate_table_text_in_prose_chunks():
    """Nội dung bảng E-204 chỉ nằm trong table chunk, không bị lặp lại trong các prose chunk."""
    target_pdf = SOPS_DIR / "SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf"
    parsed_doc = parse_pdf_document(target_pdf)
    chunks = chunk_document(parsed_doc)

    prose_chunks = [c for c in chunks if not c["is_table"]]
    table_chunks = [c for c in chunks if c["is_table"]]

    assert len(table_chunks) == 1
    assert "E-204" in table_chunks[0]["content"]
    assert "Run Feeder Feed Test on HMI screen." in table_chunks[0]["content"]

    for pc in prose_chunks:
        assert "Run Feeder Feed Test on HMI screen." not in pc["content"]
        assert "Feeder ID Comm" not in pc["content"]


def test_section_titles_accurate_for_tables():
    """section_title của bảng phải phản ánh mục ngay phía trên bảng hoặc kế thừa từ trang trước, không bắt nhầm bước thao tác."""
    feeder_doc = parse_pdf_document(SOPS_DIR / "SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf")
    feeder_chunks = chunk_document(feeder_doc)
    feeder_table = next(c for c in feeder_chunks if c["is_table"])
    assert "5. Run Feeder Feed Test" not in feeder_table["section_title"]
    assert "FEEDER TROUBLESHOOTING" in feeder_table["section_title"]

    smt_doc = parse_pdf_document(SOPS_DIR / "SOP_SMT_001_Pick_And_Place_Machine_Troubleshooting.pdf")
    smt_chunks = chunk_document(smt_doc)
    smt_page2_table = next(c for c in smt_chunks if c["is_table"] and c["page_number"] == 2)
    assert "DAILY PREVENTIVE MAINTENANCE" not in smt_page2_table["section_title"]
    assert "ERROR CODE MATRIX" in smt_page2_table["section_title"]
