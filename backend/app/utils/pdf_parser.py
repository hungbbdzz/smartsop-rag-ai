import hashlib
import logging
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple, Union

import pdfplumber

logger = logging.getLogger("smartsop.pdf_parser")

_DATA_ROW_CODE_RE = re.compile(r"^(E-\d+|ALM-|PCB-|WAVE|\d+)", re.IGNORECASE)
_HEADING_NUMBER_RE = re.compile(r"^(\d+(\.\d+)*)\.?\s+([A-ZÀ-Ỹ0-9\s\-_/&]+)$", re.IGNORECASE)


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


def _is_inside_any_bbox(obj: Dict[str, Any], bboxes: List[Tuple[float, float, float, float]]) -> bool:
    """Kiểm tra tâm của một đối tượng pdfplumber có nằm bên trong vùng bảng biểu nào không."""
    if not bboxes:
        return False
    if "x0" not in obj or "x1" not in obj or "top" not in obj or "bottom" not in obj:
        return False
    cx = (obj["x0"] + obj["x1"]) / 2.0
    cy = (obj["top"] + obj["bottom"]) / 2.0
    for x0, top, x1, bottom in bboxes:
        if x0 <= cx <= x1 and top <= cy <= bottom:
            return True
    return False


def format_table_to_markdown(
    table: List[List[Optional[Any]]],
    fallback_headers: Optional[List[str]] = None,
    force_fallback: bool = False,
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

    first_cell_str = str(table[0][0]).strip() if table[0] and table[0][0] is not None else ""
    is_data_row = force_fallback or bool(_DATA_ROW_CODE_RE.match(first_cell_str))

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

    for row in data_rows:
        clean_row = []
        for i in range(num_cols):
            cell_val = row[i] if i < len(row) else ""
            clean_row.append(_clean_cell(cell_val, replace_newlines_with="<br/>"))
        md_lines.append("| " + " | ".join(clean_row) + " |")

    return "\n".join(md_lines)


def _detect_headings_on_page(
    page: Any,
    page_num: int,
    min_font_size: float = 12.0,
) -> List[Dict[str, Any]]:
    """Dò tìm tiêu đề H1/H2/H3 trên một trang pdfplumber (đã loại bỏ vùng bảng biểu)."""
    words = page.extract_words(extra_attrs=["fontname", "size"])
    if not words:
        return []

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

    headings: List[Dict[str, Any]] = []
    for line in lines:
        line_text = " ".join(w["text"] for w in line).strip()
        if not line_text or len(line_text) < 3:
            continue

        avg_size = sum(w.get("size", 10.0) for w in line) / len(line)
        is_bold = any("bold" in w.get("fontname", "").lower() for w in line)
        line_top = min(w["top"] for w in line)

        is_heading = False
        level = 2

        if avg_size >= 14.0:
            is_heading = True
            level = 1
        elif avg_size >= min_font_size and is_bold:
            is_heading = True
            level = 2
        elif _HEADING_NUMBER_RE.match(line_text) and (is_bold or avg_size >= 11.0):
            is_heading = True
            level = 2 if avg_size >= 11.5 else 3

        if is_heading:
            headings.append({
                "page_number": page_num,
                "text": line_text,
                "level": level,
                "font_size": round(avg_size, 1),
                "is_bold": is_bold,
                "top": round(line_top, 2),
            })

    return headings


def _is_continuation_table(
    table: List[List[Optional[Any]]],
    t_idx: int,
    table_top: Optional[float],
    last_seen_headers: Optional[List[str]],
    headings_on_page: List[Dict[str, Any]],
) -> bool:
    """
    Xác định bảng trên trang hiện tại có phải là bảng nối tiếp từ trang trước hay không.
    Xử lý cả trường hợp ô đầu khớp mã lỗi (E-112) lẫn trường hợp bảng chỉ có 1 hàng dữ liệu
    hoặc hàng đầu là mô tả dài ở ngay đầu trang (VD: 'Voiding in BGA/QFN' trên SOP_REFLOW_002).
    """
    if not table or not table[0] or not last_seen_headers:
        return False

    num_cols = max(len(row) for row in table)
    if len(last_seen_headers) != num_cols:
        return False

    row0_cleaned = [_clean_cell(table[0][i] if i < len(table[0]) else "") for i in range(num_cols)]
    if row0_cleaned == last_seen_headers:
        return False

    first_cell_str = str(table[0][0]).strip() if table[0][0] is not None else ""
    if _DATA_ROW_CODE_RE.match(first_cell_str):
        return True

    headings_above = (
        [h for h in headings_on_page if h["top"] < table_top]
        if table_top is not None
        else headings_on_page
    )
    if t_idx == 0 and not headings_above:
        max_cell_len = max((len(c) for c in row0_cleaned), default=0)
        if len(table) == 1 or max_cell_len > 50:
            return True

    return False


def _extract_tables_on_page(
    page: Any,
    page_num: int,
    found_tables: List[Any],
    last_seen_headers: Optional[List[str]],
    headings_on_page: List[Dict[str, Any]],
    prev_section: str,
) -> Tuple[List[Dict[str, Any]], Optional[List[str]]]:
    """Bóc tách toàn bộ bảng biểu trên một trang thành Markdown kèm kế thừa Header & section."""
    page_tables: List[Dict[str, Any]] = []
    sorted_tables = sorted(found_tables, key=lambda t: t.bbox[1])

    for t_idx, t_obj in enumerate(sorted_tables):
        table = t_obj.extract()
        if not table or len(table) < 1:
            continue
        if len(table) == 1 and all(not cell for cell in table[0]):
            continue

        num_cols = max(len(row) for row in table)
        table_top = t_obj.bbox[1] if t_obj.bbox else None
        is_cont = _is_continuation_table(
            table=table,
            t_idx=t_idx,
            table_top=table_top,
            last_seen_headers=last_seen_headers,
            headings_on_page=headings_on_page,
        )

        current_fallback = last_seen_headers if is_cont else None
        md_table = format_table_to_markdown(
            table,
            fallback_headers=current_fallback,
            force_fallback=is_cont,
        )
        if not md_table.strip():
            continue

        if is_cont and current_fallback:
            headers = list(current_fallback)
        else:
            headers = [_clean_cell(c) for c in table[0]]
            if any(h != "" for h in headers):
                last_seen_headers = headers

        # Chọn tiêu đề gần nhất nằm PHÍA TRÊN bảng; nếu không có thì kế thừa section trang trước
        headings_above = (
            [h for h in headings_on_page if h["top"] < table_top]
            if table_top is not None
            else []
        )
        section_title = headings_above[-1]["text"] if headings_above else prev_section

        page_tables.append({
            "page_number": page_num,
            "table_index": t_idx,
            "markdown": md_table,
            "rows_count": len(table),
            "cols_count": num_cols,
            "headers": headers,
            "raw_table": table,
            "section_title": section_title,
            "top": round(table_top, 2) if table_top is not None else 0.0,
        })

    return page_tables, last_seen_headers


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

    tables_data: List[Dict[str, Any]] = []
    last_seen_headers: Optional[List[str]] = None
    current_section = "Mở đầu / Giới thiệu chung"

    with pdfplumber.open(path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            page_num = page_idx + 1
            try:
                found_tables = page.find_tables()
            except Exception as e:
                logger.warning(f"Lỗi tìm bảng ở trang {page_num} file {path.name}: {e}")
                found_tables = []

            bboxes = [t.bbox for t in found_tables]
            non_table_page = page.filter(lambda obj: not _is_inside_any_bbox(obj, bboxes)) if bboxes else page
            page_headings = _detect_headings_on_page(non_table_page, page_num)

            page_tables, last_seen_headers = _extract_tables_on_page(
                page=page,
                page_num=page_num,
                found_tables=found_tables,
                last_seen_headers=last_seen_headers,
                headings_on_page=page_headings,
                prev_section=current_section,
            )
            tables_data.extend(page_tables)

            if page_headings:
                current_section = page_headings[-1]["text"]

    return tables_data


def detect_headings(
    pdf_path: Union[str, Path],
    min_font_size: float = 12.0,
) -> List[Dict[str, Any]]:
    """
    Dò tìm các tiêu đề (Headings H1, H2, H3) trong tài liệu PDF dựa trên kích thước font,
    định dạng chữ đậm và mẫu số thứ tự mục (loại trừ vùng bên trong bảng biểu).
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy tệp PDF tại: {path.resolve()}")

    headings: List[Dict[str, Any]] = []
    with pdfplumber.open(path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            page_num = page_idx + 1
            try:
                found_tables = page.find_tables()
            except Exception:
                found_tables = []
            bboxes = [t.bbox for t in found_tables]
            non_table_page = page.filter(lambda obj: not _is_inside_any_bbox(obj, bboxes)) if bboxes else page
            headings.extend(_detect_headings_on_page(non_table_page, page_num, min_font_size=min_font_size))

    return headings


def parse_pdf_document(pdf_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Hàm tổng hợp toàn diện bóc tách tài liệu PDF kỹ thuật (chỉ mở tệp PDF 1 lần):
    - Trích xuất metadata (sha256, dung lượng, số trang).
    - Tách riêng văn bản ngoài bảng (prose_text) và bảng biểu Markdown để tránh trùng lặp khi chunking.
    - Phát hiện tiêu đề (loại trừ vùng bảng) và tự động chèn prefix Markdown ('## ', '### ').
    - Kế thừa tiêu đề bảng và section_title chuẩn xác qua ranh giới trang.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy tệp PDF tại: {path.resolve()}")

    file_bytes = path.read_bytes()
    file_hash = hashlib.sha256(file_bytes).hexdigest()

    parsed_pages: List[Dict[str, Any]] = []
    all_tables: List[Dict[str, Any]] = []
    total_headings = 0
    last_seen_headers: Optional[List[str]] = None
    current_section = "Mở đầu / Giới thiệu chung"

    with pdfplumber.open(path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            page_num = page_idx + 1
            raw_text = (page.extract_text() or "").strip()

            try:
                found_tables = page.find_tables()
            except Exception as e:
                logger.warning(f"Lỗi tìm bảng ở trang {page_num} file {path.name}: {e}")
                found_tables = []

            bboxes = [t.bbox for t in found_tables]
            non_table_page = page.filter(lambda obj: not _is_inside_any_bbox(obj, bboxes)) if bboxes else page

            prose_text = (non_table_page.extract_text() or "").strip() if bboxes else raw_text
            page_headings = _detect_headings_on_page(non_table_page, page_num)
            total_headings += len(page_headings)

            page_tables, last_seen_headers = _extract_tables_on_page(
                page=page,
                page_num=page_num,
                found_tables=found_tables,
                last_seen_headers=last_seen_headers,
                headings_on_page=page_headings,
                prev_section=current_section,
            )
            all_tables.extend(page_tables)

            annotated_prose = prose_text
            for h in page_headings:
                h_text = h["text"]
                prefix = "## " if h["level"] <= 2 else "### "
                pattern = re.compile(rf"(^|\n)({re.escape(h_text)})(\n|$)", re.MULTILINE)
                if pattern.search(annotated_prose):
                    annotated_prose = pattern.sub(rf"\1{prefix}\2\3", annotated_prose, count=1)

            if page_tables:
                table_md_blocks = "\n\n".join(t["markdown"] for t in page_tables)
                integrated_content = (
                    f"{annotated_prose}\n\n### BẢNG TRA CỨU MÃ LỖI & THÔNG SỐ (MARKDOWN):\n{table_md_blocks}".strip()
                )
            else:
                integrated_content = annotated_prose

            parsed_pages.append({
                "page_number": page_num,
                "raw_text": raw_text,
                "prose_text": prose_text,
                "annotated_prose": annotated_prose,
                "integrated_content": integrated_content,
                "has_tables": len(page_tables) > 0,
                "tables_count": len(page_tables),
                "tables": page_tables,
                "headings": [h["text"] for h in page_headings],
            })

            if page_headings:
                current_section = page_headings[-1]["text"]

    return {
        "file_name": path.name,
        "file_path": str(path.resolve()),
        "file_hash": file_hash,
        "file_size": len(file_bytes),
        "total_pages": len(parsed_pages),
        "total_tables": len(all_tables),
        "total_headings": total_headings,
        "pages": parsed_pages,
        "all_tables": all_tables,
    }
