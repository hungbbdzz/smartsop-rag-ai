from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.sop_document import SOPDocument


class SOPChunk(Base, TimestampMixin):
    """
    Bảng đối soát metadata của các vector phân đoạn.
    Vector embeddings được lưu trữ tại ChromaDB (với ID = chroma_id).
    Bảng này phục vụ đối soát, thống kê và xóa đồng bộ khi gỡ bỏ SOP.
    """
    __tablename__ = "sop_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sop_documents.id", ondelete="CASCADE"), nullable=False
    )
    chroma_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    page_num: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    section_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    char_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Quan hệ
    document: Mapped["SOPDocument"] = relationship("SOPDocument", back_populates="chunks")

    def __repr__(self) -> str:
        return f"<SOPChunk chroma_id={self.chroma_id} page={self.page_num}>"

