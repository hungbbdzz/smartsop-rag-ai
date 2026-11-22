import re
from typing import Any, Dict, List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter

_MD_HEADING_RE = re.compile(r"^(?:##|###)\s+(.+)$", re.MULTILINE)


class TableAwareChunker:
    """
    Bộ phân đoạn ngữ nghĩa tối ưu cho tài liệu kỹ thuật nhà máy (Table-Aware Semantic Chunker):
    1. Bảng biểu ngắn (<= 2000 ký tự): Giữ nguyên vẹn 100% trong 1 chunk duy nhất, không chia cắt.
    2. Bảng biểu dài (> 2000 ký tự): Tách theo từng nhóm dòng, LUÔN LẶP LẠI DÒNG TIÊU ĐỀ CỘT để bảo toàn ngữ nghĩa mã lỗi.
    3. Không bao giờ cắt xẻ ngang lưng một dòng mã lỗi.
    4. Văn xuôi thông thường: Tách bằng RecursiveCharacterTextSplitter từ annotated_prose (đã loại bỏ nội dung bảng để tránh lặp).
    """

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 150,
        max_table_chunk_size: int = 2000,
        rows_per_table_chunk: int = 4,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_table_chunk_size = max_table_chunk_size
        self.rows_per_table_chunk = rows_per_table_chunk

        self.prose_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
        )

    def split_table_to_chunks(
        self,
        markdown_table: str,
        page_number: int,
        section_title: str = "Bảng thông số & Mã lỗi kỹ thuật",
        raw_headers: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Phân đoạn một bảng biểu Markdown:
        - Bảng ngắn: Trả về 1 chunk duy nhất.
        - Bảng dài: Chia thành nhiều chunk, mỗi chunk lặp lại dòng Header và Separator.
        """
        table_lines = [line.strip() for line in markdown_table.strip().split("\n") if line.strip()]
        if not table_lines:
            return []

        if len(markdown_table) <= self.max_table_chunk_size or len(table_lines) <= 4:
            return [{
                "page_number": page_number,
                "section_title": section_title,
                "content": markdown_table.strip(),
                "char_count": len(markdown_table.strip()),
                "is_table": True,
                "table_headers": raw_headers or [],
            }]

        header_line = table_lines[0]
        has_separator = len(table_lines) > 1 and "---" in table_lines[1]
        num_cols = max(header_line.count("|") - 1, 1)
        separator_line = (
            table_lines[1]
            if has_separator
            else "| " + " | ".join(["---"] * num_cols) + " |"
        )
        data_rows = table_lines[2:] if has_separator else table_lines[1:]

        chunks = []
        for i in range(0, len(data_rows), self.rows_per_table_chunk):
            row_group = data_rows[i : i + self.rows_per_table_chunk]
            chunk_lines = [header_line, separator_line] + row_group
            chunk_content = "\n".join(chunk_lines)

            chunks.append({
                "page_number": page_number,
                "section_title": f"{section_title} (Phần {len(chunks) + 1})",
                "content": chunk_content,
                "char_count": len(chunk_content),
                "is_table": True,
                "table_headers": raw_headers or [],
            })

        return chunks

    def chunk_parsed_document(self, parsed_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Phân đoạn toàn bộ tài liệu đã được bóc tách từ pdf_parser.
        Tách riêng văn xuôi (`annotated_prose`) và bảng biểu (`tables`) để không lặp dữ liệu
        và giữ chính xác `section_title` theo tiêu đề Markdown.
        """
        all_chunks: List[Dict[str, Any]] = []
        global_chunk_idx = 0
        current_section = "Mở đầu / Giới thiệu chung"

        for page in parsed_doc.get("pages", []):
            page_num = page["page_number"]
            prose_source = page.get("annotated_prose") if "annotated_prose" in page else page.get("raw_text", "")
            page_tables = page.get("tables", [])
            page_headings = page.get("headings", [])

            # 1. Xử lý văn xuôi đã tách khỏi vùng bảng (tận dụng separator \n## , \n### )
            if prose_source:
                prose_subtexts = self.prose_splitter.split_text(prose_source)
                for subtext in prose_subtexts:
                    clean_subtext = subtext.strip()
                    if not clean_subtext:
                        continue

                    md_headings = _MD_HEADING_RE.findall(clean_subtext)
                    chunk_section = md_headings[0].strip() if md_headings else current_section
                    if md_headings:
                        current_section = md_headings[-1].strip()

                    all_chunks.append({
                        "chunk_index": global_chunk_idx,
                        "page_number": page_num,
                        "section_title": chunk_section,
                        "content": clean_subtext,
                        "char_count": len(clean_subtext),
                        "is_table": False,
                        "table_headers": None,
                    })
                    global_chunk_idx += 1

            # 2. Xử lý các bảng biểu trên trang (Table-Aware)
            for t_info in page_tables:
                md_table = t_info.get("markdown", "")
                raw_headers = t_info.get("headers", [])
                table_section = t_info.get("section_title") or current_section
                table_title = f"{table_section} - Bảng tra cứu"

                table_chunks = self.split_table_to_chunks(
                    markdown_table=md_table,
                    page_number=page_num,
                    section_title=table_title,
                    raw_headers=raw_headers,
                )

                for t_chunk in table_chunks:
                    t_chunk["chunk_index"] = global_chunk_idx
                    all_chunks.append(t_chunk)
                    global_chunk_idx += 1

            if page_headings:
                current_section = page_headings[-1]

        return all_chunks


def chunk_document(
    parsed_doc: Dict[str, Any],
    chunk_size: int = 800,
    chunk_overlap: int = 150,
) -> List[Dict[str, Any]]:
    """
    Hàm tiện ích cấp cao phân đoạn tài liệu kỹ thuật SOP với Table-Aware Chunking.
    """
    chunker = TableAwareChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return chunker.chunk_parsed_document(parsed_doc)
