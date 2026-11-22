import hashlib
import logging
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Union

import pdfplumber

logger = logging.getLogger("smartsop.pdf_parser")


def _clean_cell(val: Optional[Any], replace_newlines_with: str = " ") -> str:
    """Làm sạch ký tự trong ô bảng biểu: chuẩn hóa khoảng trắng và ngắt dòng."""
    if val is None:
        return ""
    text = str(val).strip()
    if replace_newlines_with == " ":
        text = re.sub(r"\s*\n\s*", " ", text)
    else:
        text = text.replace("\n", replace_newlines_with)
    # Thoát ký tự pipe '|' để không làm hỏng cấu trúc Markdown table
    text = text.replace("|", "\\|")
    return text


def format_table_to_markdown(
    table: List[List[Optional[Any]]],
    fallback_headers: Optional[List[str]] = None,
) -> str:
    """
    Chuyển đổi ma trận bảng dữ liệu (từ pdfplumber) thành bảng định dạng Markdown chuẩn.
    Tự động kế thừa hoặc tạo tiêu đề nếu hàng đầu tiên là hàng dữ liệu (bảng nối tiếp qua trang).
    """
    if not table or len(table) < 1:
        return ""

    num_cols = max(len(row) for row in table)
    if num_cols == 0:
        return ""

    # Kiểm tra xem hàng đầu tiên có phải là hàng dữ liệu mã lỗi nối tiếp qua trang không
    first_cell_str = str(table[0][0]).strip() if table[0] and table[0][0] is not None else ""
    is_data_row = bool(re.match(r"^(E-\d+|ALM-|PCB-|WAVE|\d+)", first_cell_str, re.IGNORECASE))

    if is_data_row and fallback_headers and len(fallback_headers) == num_cols:
        headers = fallback_headers
        data_rows = table
    else:
        header_row = table[0]
        headers = [_clean_cell(col if i < len(header_row) else "") for i, col in enumerate(header_row)]
        if all(h == "" for h in headers):
            if fallback_headers and len(fallback_headers) == num_cols:
                headers = fallback_headers
            else:
                headers = [f"Cột {i+1}" for i in range(num_cols)]
        data_rows = table[1:]

    md_lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * num_cols) + " |",
    ]

    # Các dòng dữ liệu
    for row in data_rows:
        clean_row = []
        for i in range(num_cols):
            cell_val = row[i] if i < len(row) else ""
            clean_row.append(_clean_cell(cell_val, replace_newlines_with="<br/>"))
        md_lines.append("| " + " | ".join(clean_row) + " |")

    return "\n".join(md_lines)


def extract_text_by_page(pdf_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Trích xuất toàn bộ văn bản của tài liệu PDF theo từng trang.
    Trả về danh sách đối tượng chứa số trang, văn bản thuần, và số lượng ký tự.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy tệp PDF tại: {path.resolve()}")

    pages_data = []
    with pdfplumber.open(path) as pdf:
        for idx, page in enumerate(pdf.pages):
            page_num = idx + 1
            raw_text = page.extract_text() or ""
            cleaned_text = raw_text.strip()
            pages_data.append({
                "page_number": page_num,
                "text": cleaned_text,
                "char_count": len(cleaned_text),
                "word_count": len(cleaned_text.split()),
            })

    return pages_data


def extract_tables_as_markdown(pdf_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Bóc tách toàn bộ bảng biểu trong tài liệu PDF và chuyển đổi thành định dạng Markdown.
    Hỗ trợ kế thừa tiêu đề giữa các trang khi bảng bị ngắt đôi (Table Continuation across pages).
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy tệp PDF tại: {path.resolve()}")

    tables_data = []
    last_seen_headers: Optional[List[str]] = None

    with pdfplumber.open(path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            page_num = page_idx + 1
            try:
                tables = page.extract_tables()
            except Exception as e:
                logger.warning(f"Lỗi trích xuất bảng ở trang {page_num} file {path.name}: {e}")
                tables = []

            for t_idx, table in enumerate(tables):
                if not table or len(table) < 1:
                    continue
                if len(table) == 1 and all(not cell for cell in table[0]):
                    continue

                num_cols = max(len(row) for row in table)
                first_cell_str = str(table[0][0]).strip() if table[0] and table[0][0] is not None else ""
                is_data_row = bool(re.match(r"^(E-\d+|ALM-|PCB-|WAVE|\d+)", first_cell_str, re.IGNORECASE))

                # Kế thừa headers nếu hàng đầu tiên là data row
                current_fallback = None
                if is_data_row and last_seen_headers and len(last_seen_headers) == num_cols:
                    current_fallback = last_seen_headers

                md_table = format_table_to_markdown(table, fallback_headers=current_fallback)
                if not md_table.strip():
                    continue

                if is_data_row and current_fallback:
                    headers = current_fallback
                else:
                    headers = [_clean_cell(c) for c in table[0]]
                    if not is_data_row and any(h != "" for h in headers):
                        last_seen_headers = headers

                tables_data.append({
                    "page_number": page_num,
                    "table_index": t_idx,
                    "markdown": md_table,
                    "rows_count": len(table),
                    "cols_count": num_cols,
                    "headers": headers,
                    "raw_table": table,
                })

    return tables_data


def detect_headings(
    pdf_path: Union[str, Path],
    min_font_size: float = 12.0
) -> List[Dict[str, Any]]:
    """
    Dò tìm các tiêu đề (Headings H1, H2, H3) trong tài liệu PDF dựa trên:
    1. Kích thước font chữ (font_size >= 12.0 pt).
    2. Định dạng chữ đậm (Bold).
    3. Mẫu số thứ tự mục công nghiệp (VD: '1. PURPOSE', '2. WORKFLOW', '3.1').
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy tệp PDF tại: {path.resolve()}")

    headings = []
    heading_pattern = re.compile(r"^(\d+(\.\d+)*)\.?\s+([A-ZÀ-Ỹ0-9\s\-_/&]+)$", re.IGNORECASE)

    with pdfplumber.open(path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            page_num = page_idx + 1
            words = page.extract_words(extra_attrs=["fontname", "size"])
            if not words:
                continue

            lines: List[List[Dict[str, Any]]] = []
            current_line: List[Dict[str, Any]] = []
            current_top: Optional[float] = None

            for w in words:
                w_top = w["top"]
                if current_top is None or abs(w_top - current_top) <= 3.0:
                    current_line.append(w)
                    current_top = w_top
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = [w]
                    current_top = w_top
            if current_line:
                lines.append(current_line)

            for line in lines:
                line_text = " ".join(w["text"] for w in line).strip()
                if not line_text or len(line_text) < 3:
                    continue

                avg_size = sum(w.get("size", 10.0) for w in line) / len(line)
                is_bold = any("bold" in w.get("fontname", "").lower() for w in line)

                is_heading = False
                level = 2

                if avg_size >= 14.0:
                    is_heading = True
                    level = 1
                elif avg_size >= min_font_size and is_bold:
                    is_heading = True
                    level = 2
                elif heading_pattern.match(line_text) and (is_bold or avg_size >= 11.0):
                    is_heading = True
                    level = 2 if avg_size >= 11.5 else 3

                if is_heading:
                    headings.append({
                        "page_number": page_num,
                        "text": line_text,
                        "level": level,
                        "font_size": round(avg_size, 1),
                        "is_bold": is_bold,
                    })

    return headings


def parse_pdf_document(pdf_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Hàm tổng hợp toàn diện bóc tách tài liệu PDF kỹ thuật:
    - Trích xuất metadata (sha256, dung lượng, số trang).
    - Trích xuất toàn bộ bảng thành Markdown.
    - Phát hiện tiêu đề và tự động chèn prefix Markdown ('## ', '### ').
    - Tích hợp nội dung từng trang với bảng Markdown hoàn chỉnh.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy tệp PDF tại: {path.resolve()}")

    file_bytes = path.read_bytes()
    file_hash = hashlib.sha256(file_bytes).hexdigest()

    pages_text = extract_text_by_page(path)
    tables_list = extract_tables_as_markdown(path)
    headings_list = detect_headings(path)

    tables_by_page: Dict[int, List[Dict[str, Any]]] = {}
    for t in tables_list:
        p_num = t["page_number"]
        tables_by_page.setdefault(p_num, []).append(t)

    headings_by_page: Dict[int, List[Dict[str, Any]]] = {}
    for h in headings_list:
        p_num = h["page_number"]
        headings_by_page.setdefault(p_num, []).append(h)

    parsed_pages = []
    for p_info in pages_text:
        page_num = p_info["page_number"]
        page_text = p_info["text"]
        page_tables = tables_by_page.get(page_num, [])
        page_headings = headings_by_page.get(page_num, [])

        annotated_text = page_text
        for h in page_headings:
            h_text = h["text"]
            prefix = "## " if h["level"] <= 2 else "### "
            pattern = re.compile(rf"(^|\n)({re.escape(h_text)})(\n|$)", re.MULTILINE)
            if pattern.search(annotated_text):
                annotated_text = pattern.sub(rf"\1{prefix}\2\3", annotated_text, count=1)

        if page_tables:
            table_md_blocks = "\n\n".join(t["markdown"] for t in page_tables)
            integrated_content = f"{annotated_text}\n\n### BẢNG TRA CỨU MÃ LỖI & THÔNG SỐ (MARKDOWN):\n{table_md_blocks}"
        else:
            integrated_content = annotated_text

        parsed_pages.append({
            "page_number": page_num,
            "raw_text": page_text,
            "integrated_content": integrated_content,
            "has_tables": len(page_tables) > 0,
            "tables_count": len(page_tables),
            "tables": page_tables,
            "headings": [h["text"] for h in page_headings],
        })

    return {
        "file_name": path.name,
        "file_path": str(path.resolve()),
        "file_hash": file_hash,
        "file_size": len(file_bytes),
        "total_pages": len(parsed_pages),
        "total_tables": len(tables_list),
        "total_headings": len(headings_list),
        "pages": parsed_pages,
        "all_tables": tables_list,
    }
