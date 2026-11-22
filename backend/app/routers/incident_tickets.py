from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.models.incident_ticket import IncidentTicket, TicketPriority, TicketStatus
from app.models.machine import Machine
from app.models.sop_document import SOPDocument
from app.models.user import User, UserRole
from app.schemas.incident_ticket import TicketCreate, TicketResponse, TicketUpdate
from app.services.ticket_service import suggest_sop_for_incident

router = APIRouter(
    prefix="/incident_tickets",
    tags=["Incident Tickets"],
)

# Ma trận chuyển trạng thái hợp lệ của phiếu sự cố
# Ràng buộc: Tuyệt đối không cho phép OPEN nhảy cóc thẳng sang RESOLVED
ALLOWED_STATUS_TRANSITIONS = {
    TicketStatus.OPEN: {TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.CLOSED},
    TicketStatus.IN_PROGRESS: {TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED, TicketStatus.OPEN},
    TicketStatus.RESOLVED: {TicketStatus.RESOLVED, TicketStatus.CLOSED, TicketStatus.IN_PROGRESS},
    TicketStatus.CLOSED: {TicketStatus.CLOSED, TicketStatus.IN_PROGRESS},
}


@router.get(
    "",
    response_model=List[TicketResponse],
    summary="Xem danh sách phiếu sự cố (Hỗ trợ lọc theo thiết bị, trạng thái, mức độ ưu tiên)",
)
async def list_incident_tickets(
    machine_id: Optional[str] = Query(None, description="Lọc theo ID thiết bị"),
    status: Optional[TicketStatus] = Query(None, description="Lọc theo trạng thái phiếu"),
    priority: Optional[TicketPriority] = Query(None, description="Lọc theo mức độ ưu tiên"),
    error_code: Optional[str] = Query(None, description="Lọc theo mã lỗi (chính xác)"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(IncidentTicket)
    if machine_id:
        stmt = stmt.where(IncidentTicket.machine_id == machine_id)
    if status:
        stmt = stmt.where(IncidentTicket.status == status)
    if priority:
        stmt = stmt.where(IncidentTicket.priority == priority)
    if error_code:
        stmt = stmt.where(IncidentTicket.error_code == error_code)

    stmt = stmt.order_by(IncidentTicket.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get(
    "/suggest-sop",
    summary="Gợi ý nhanh tài liệu SOP phù hợp cho mã lỗi và mô tả sự cố",
)
async def preview_sop_suggestion(
    error_code: str = Query("", description="Mã lỗi kỹ thuật (VD: E-204)"),
    description: str = Query("", description="Mô tả hiện tượng sự cố"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    suggestion = await suggest_sop_for_incident(
        error_code=error_code,
        description=description,
        db=db,
    )
    return {
        "found": suggestion is not None,
        "suggestion": suggestion,
    }


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Xem chi tiết một phiếu sự cố",
)
async def get_incident_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(IncidentTicket).where(IncidentTicket.id == ticket_id)
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy phiếu sự cố với ID '{ticket_id}'",
        )
    return ticket


@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo phiếu báo cáo sự cố máy móc (Yêu cầu vai trò Kỹ sư ca, Quản đốc hoặc Admin)",
)
async def create_incident_ticket(
    ticket_in: TicketCreate,
    current_user: User = Depends(
        require_roles([UserRole.SHIFT_ENGINEER, UserRole.FACTORY_MANAGER, UserRole.ADMIN])
    ),
    db: AsyncSession = Depends(get_db),
):
    # 1. Kiểm tra máy móc có tồn tại trong CSDL không
    machine_stmt = select(Machine).where(Machine.id == ticket_in.machine_id)
    machine_res = await db.execute(machine_stmt)
    machine = machine_res.scalar_one_or_none()
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy thiết bị với ID '{ticket_in.machine_id}'",
        )

    suggested_sop_id = ticket_in.suggested_sop_id
    suggested_page = ticket_in.suggested_page
    suggested_snippet = ticket_in.suggested_snippet

    # 2. Kiểm tra nếu người dùng tự gán tài liệu SOP gợi ý; ngược lại tự động tìm bằng RAG
    if suggested_sop_id:
        sop_stmt = select(SOPDocument).where(SOPDocument.id == suggested_sop_id)
        sop_res = await db.execute(sop_stmt)
        if not sop_res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy tài liệu SOP gợi ý với ID '{suggested_sop_id}'",
            )
    else:
        suggestion = await suggest_sop_for_incident(
            error_code=ticket_in.error_code,
            description=ticket_in.description,
            db=db,
        )
        if suggestion:
            suggested_sop_id = suggestion["suggested_sop_id"]
            suggested_page = suggestion["suggested_page"]
            suggested_snippet = suggestion["suggested_snippet"]

    # 3. Tạo mã phiếu tự động nếu chưa có
    ticket_code = ticket_in.ticket_code
    if not ticket_code:
        now_str = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        ticket_code = f"INC-{now_str}-{uuid4().hex[:4].upper()}"
    else:
        # Kiểm tra trùng mã phiếu nếu người dùng tự cung cấp
        code_stmt = select(IncidentTicket).where(IncidentTicket.ticket_code == ticket_code)
        code_res = await db.execute(code_stmt)
        if code_res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Mã phiếu sự cố '{ticket_code}' đã tồn tại trong hệ thống",
            )

    ticket = IncidentTicket(
        ticket_code=ticket_code,
        machine_id=ticket_in.machine_id,
        reported_by=current_user.id,
        error_code=ticket_in.error_code,
        description=ticket_in.description,
        priority=ticket_in.priority,
        status=TicketStatus.OPEN,
        suggested_sop_id=suggested_sop_id,
        suggested_page=suggested_page,
        suggested_snippet=suggested_snippet,
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return ticket


@router.patch(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Cập nhật tiến độ xử lý phiếu sự cố, kiểm soát chuyển trạng thái",
)
async def update_incident_ticket(
    ticket_id: str,
    ticket_in: TicketUpdate,
    current_user: User = Depends(
        require_roles([UserRole.SHIFT_ENGINEER, UserRole.FACTORY_MANAGER, UserRole.ADMIN])
    ),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(IncidentTicket).where(IncidentTicket.id == ticket_id)
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy phiếu sự cố với ID '{ticket_id}'",
        )

    # Kiểm tra quy tắc chuyển đổi trạng thái (State Machine)
    if ticket_in.status is not None and ticket_in.status != ticket.status:
        current_status = ticket.status
        target_status = ticket_in.status

        # Quy tắc kiểm soát nghiêm ngặt Gate Test 1.3:
        # Không cho phép chuyển thẳng từ OPEN sang RESOLVED
        if current_status == TicketStatus.OPEN and target_status == TicketStatus.RESOLVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể chuyển trạng thái trực tiếp từ OPEN sang RESOLVED. Phiếu sự cố phải được chuyển sang IN_PROGRESS trước khi giải quyết.",
            )

        allowed_targets = ALLOWED_STATUS_TRANSITIONS.get(current_status, set())
        if target_status not in allowed_targets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Chuyển đổi trạng thái không hợp lệ: từ '{current_status}' sang '{target_status}'.",
            )

        ticket.status = target_status

        # Tự động cập nhật mốc thời gian xử lý phục vụ tính toán MTTR
        now = datetime.now(timezone.utc)
        if target_status == TicketStatus.IN_PROGRESS and not ticket.started_at:
            ticket.started_at = now
        elif target_status == TicketStatus.RESOLVED:
            ticket.resolved_at = now

    update_data = ticket_in.model_dump(exclude_unset=True, exclude={"status"})
    for field, val in update_data.items():
        setattr(ticket, field, val)

    await db.commit()
    await db.refresh(ticket)
    return ticket


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa phiếu sự cố (Chỉ Admin)",
)
async def delete_incident_ticket(
    ticket_id: str,
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(IncidentTicket).where(IncidentTicket.id == ticket_id)
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy phiếu sự cố với ID '{ticket_id}'",
        )

    await db.delete(ticket)
    await db.commit()
    return {"message": f"Đã xóa thành công phiếu sự cố '{ticket.ticket_code}'"}

