from typing import Any, Dict, List

REFUSAL_MESSAGE = (
    "Quy trình hiện tại chưa ghi nhận mã lỗi hoặc thao tác này. "
    "Vui lòng dừng máy và liên hệ Kỹ sư trưởng ca trực hoặc Bộ phận Bảo trì Thiết bị."
)

SYSTEM_PROMPT = f"""Bạn là Trợ lý Kỹ thuật Vận hành Thông minh của Nhà máy Sản xuất Điện tử (SmartSOP AI).
Nhiệm vụ của bạn là hỗ trợ kỹ sư ca và công nhân dây chuyền xử lý sự cố thiết bị dựa trên tài liệu Quy trình Vận hành Chuẩn (SOP) được cung cấp trong phần [NGỮ CẢNH TÀI LIỆU].

QUY TẮC BẮT BUỘC (HARD GUARDRAILS):
1. CHỈ sử dụng thông tin thực tế có trong phần [NGỮ CẢNH TÀI LIỆU] bên dưới để trả lời.
2. TUYỆT ĐỐI KHÔNG tự suy đoán, bịa đặt mã lỗi, thông số kỹ thuật hoặc các bước xử lý không có trong tài liệu.
3. Nếu [NGỮ CẢNH TÀI LIỆU] không chứa thông tin giải quyết câu hỏi, bạn PHẢI trả lời chính xác nguyên văn câu sau và không thêm thông tin ngoài lề:
   "{REFUSAL_MESSAGE}"
4. Mọi thông tin kỹ thuật đưa ra đều phải trích dẫn nguồn đúng định dạng `[Tên file - Trang X]` khớp chính xác với metadata `File` và `Trang` của ngữ cảnh đã cung cấp.
5. Trình bày câu trả lời ngắn gọn, rõ ràng theo đúng cấu trúc 4 phần:
   - 📌 **Hiện tượng / Mã lỗi**
   - 🔍 **Nguyên nhân tiềm ẩn**
   - 🛠️ **Các bước xử lý tuần tự (Step-by-step)**
   - ⚠️ **Cảnh báo an toàn & 📖 Nguồn trích dẫn** (`[Tên file - Trang X]`)"""


def format_context_blocks(chunks: List[Dict[str, Any]], max_chars: int = 8000) -> str:
    """
    Định dạng danh sách đoạn SOP truy hồi được thành khối ngữ cảnh có gắn metadata nguồn rõ ràng.
    Luôn giữ tối thiểu chunk đầu tiên và tôn trọng giới hạn `max_chars` cho các chunk tiếp theo.
    """
    if not chunks:
        return ""

    blocks: List[str] = []
    total_chars = 0

    for idx, chunk in enumerate(chunks, start=1):
        meta = chunk.get("metadata") or {}
        source_file = meta.get("source_file") or chunk.get("source_file") or "unknown.pdf"
        page_num = meta.get("page_num") or chunk.get("page_number") or 1
        section_title = meta.get("section_title") or chunk.get("section_title") or "Tài liệu SOP"
        score = chunk.get("score", 0.0)
        content = (chunk.get("content") or "").strip()

        header = (
            f"[NGUỒN {idx} | File: {source_file} | Trang: {page_num} | "
            f"Mục: {section_title} | Độ khớp: {score}]"
        )
        block = f"{header}\n{content}"

        separator_len = 2 if blocks else 0
        if blocks and (total_chars + separator_len + len(block) > max_chars):
            break

        blocks.append(block)
        total_chars += separator_len + len(block)

    return "\n\n".join(blocks)


def build_rag_prompt(
    query: str,
    chunks: List[Dict[str, Any]],
    max_context_chars: int = 8000,
) -> Dict[str, str]:
    """
    Ghép câu hỏi kỹ sư và ngữ cảnh tài liệu SOP thành cặp `system_prompt` và `user_prompt`
    sẵn sàng gửi tới LLM Provider.
    """
    context_text = format_context_blocks(chunks, max_chars=max_context_chars)
    if not context_text:
        context_text = "(Không tìm thấy đoạn tài liệu SOP phù hợp trong kho tri thức.)"

    user_prompt = (
        f"[NGỮ CẢNH TÀI LIỆU]\n{context_text}\n\n"
        f"[CÂU HỎI KỸ THUẬT]\n{query.strip()}\n\n"
        "Hãy trả lời chính xác dựa trên [NGỮ CẢNH TÀI LIỆU] theo cấu trúc 4 phần và "
        "trích dẫn nguồn đúng định dạng [Tên file - Trang X]."
    )

    return {
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": user_prompt,
        "context_text": context_text,
    }
