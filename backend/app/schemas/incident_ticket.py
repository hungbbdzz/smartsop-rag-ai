from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.incident_ticket import TicketPriority, TicketStatus


class TicketBase(BaseModel):
    machine_id: str = Field(..., description="ID của thiết bị gặp sự cố")
    error_code: str = Field(..., max_length=50, description="Mã lỗi kỹ thuật (Ví dụ: E-204, ALM-03)")
    description: str = Field(..., max_length=1000, description="Mô tả chi tiết hiện tượng sự cố")
    priority: TicketPriority = Field(default=TicketPriority.MEDIUM, description="Mức độ ưu tiên")


class TicketCreate(TicketBase):
    ticket_code: Optional[str] = Field(None, max_length=50, description="Mã phiếu sự cố (tự động tạo nếu bỏ trống)")
    suggested_sop_id: Optional[str] = Field(None, description="ID tài liệu SOP được AI gợi ý")
    suggested_page: Optional[int] = Field(None, description="Số trang tài liệu SOP được AI gợi ý")
    suggested_snippet: Optional[str] = Field(None, max_length=500, description="Đoạn trích hướng dẫn từ SOP")


class TicketUpdate(BaseModel):
    status: Optional[TicketStatus] = Field(None, description="Trạng thái mới của phiếu")
    priority: Optional[TicketPriority] = Field(None, description="Mức độ ưu tiên cập nhật")
    description: Optional[str] = Field(None, max_length=1000, description="Cập nhật mô tả sự cố")
    resolution_notes: Optional[str] = Field(None, max_length=1000, description="Ghi chú quá trình khắc phục sự cố")
    suggested_sop_id: Optional[str] = Field(None, description="ID SOP cập nhật")
    suggested_page: Optional[int] = Field(None, description="Số trang SOP cập nhật")
    suggested_snippet: Optional[str] = Field(None, max_length=500, description="Đoạn trích SOP cập nhật")


class TicketResponse(TicketBase):
    id: str
    ticket_code: str
    reported_by: Optional[str] = None
    status: TicketStatus
    suggested_sop_id: Optional[str] = None
    suggested_page: Optional[int] = None
    suggested_snippet: Optional[str] = None
    started_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

