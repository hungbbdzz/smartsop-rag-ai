from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.sop_document import IngestionStatus


class SOPDocumentBase(BaseModel):
    document_code: str = Field(..., max_length=50, description="Mã hiệu tài liệu SOP (Ví dụ: SOP-SMT-001)")
    title: str = Field(..., max_length=255, description="Tiêu đề quy trình chuẩn")
    version: str = Field(default="1.0", max_length=20, description="Phiên bản tài liệu")
    line_id: Optional[str] = Field(None, description="Dây chuyền sản xuất áp dụng")
    machine_id: Optional[str] = Field(None, description="Thiết bị máy móc áp dụng")


class SOPDocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255, description="Tiêu đề quy trình")
    version: Optional[str] = Field(None, max_length=20, description="Phiên bản tài liệu")
    line_id: Optional[str] = Field(None, description="Dây chuyền sản xuất áp dụng")
    machine_id: Optional[str] = Field(None, description="Thiết bị máy móc áp dụng")


class SOPDocumentResponse(SOPDocumentBase):
    id: str
    file_name: str
    file_path: str
    file_hash: str
    file_size: Optional[int] = None
    page_count: int
    chunk_count: int
    ingestion_status: IngestionStatus
    ingestion_error: Optional[str] = None
    uploaded_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

