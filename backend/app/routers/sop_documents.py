import hashlib
import io
import os
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

import pypdf
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.models.machine import Machine
from app.models.production_line import ProductionLine
from app.models.sop_document import IngestionStatus, SOPDocument
from app.models.user import User, UserRole
from app.schemas.sop_document import SOPDocumentResponse, SOPDocumentUpdate

router = APIRouter(
    prefix="/sop_documents",
    tags=["SOP Documents"],
)


@router.get(
    "",
    response_model=List[SOPDocumentResponse],
    summary="Xem danh mục tài liệu quy trình chuẩn (Hỗ trợ lọc theo dây chuyền, máy, trạng thái nạp vector)",
)
async def list_sop_documents(
    line_id: Optional[str] = Query(None, description="Lọc theo ID dây chuyền sản xuất"),
    machine_id: Optional[str] = Query(None, description="Lọc theo ID thiết bị"),
    status: Optional[IngestionStatus] = Query(None, description="Lọc theo trạng thái bóc tách (PENDING, PROCESSING, COMPLETED, FAILED)"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SOPDocument)
    if line_id:
        stmt = stmt.where(SOPDocument.line_id == line_id)
    if machine_id:
        stmt = stmt.where(SOPDocument.machine_id == machine_id)
    if status:
        stmt = stmt.where(SOPDocument.ingestion_status == status)

    stmt = stmt.order_by(SOPDocument.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get(
    "/{document_id}",
    response_model=SOPDocumentResponse,
    summary="Xem chi tiết thông tin metadata của một tài liệu SOP",
)
async def get_sop_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SOPDocument).where(SOPDocument.id == document_id)
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy tài liệu SOP với ID '{document_id}'",
        )
    return doc


@router.post(
    "/upload",
    response_model=SOPDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tải lên tài liệu SOP định dạng PDF, kiểm tra trùng lặp SHA-256 (Quản đốc hoặc Admin)",
)
async def upload_sop_document(
    file: UploadFile = File(..., description="File PDF quy trình kỹ thuật"),
    document_code: str = Form(..., description="Mã hiệu tài liệu SOP (Ví dụ: SOP-SMT-004)"),
    title: str = Form(..., description="Tiêu đề tài liệu"),
    version: str = Form("1.0", description="Phiên bản tài liệu"),
    line_id: Optional[str] = Form(None, description="ID dây chuyền áp dụng"),
    machine_id: Optional[str] = Form(None, description="ID thiết bị áp dụng"),
    current_user: User = Depends(
        require_roles([UserRole.FACTORY_MANAGER, UserRole.ADMIN])
    ),
    db: AsyncSession = Depends(get_db),
):
    # 1. Kiểm tra định dạng file (phải là PDF)
    filename = file.filename or "unknown.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hệ thống chỉ chấp nhận định dạng tài liệu PDF (.pdf)",
        )

    # 2. Đọc nội dung file và tính toán SHA-256 hash chống trùng lặp
    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File tải lên không có dữ liệu (0 bytes)",
        )

    file_hash = hashlib.sha256(content).hexdigest()

    # 3. GATE TEST 1.3: Kiểm tra trùng mã băm SHA-256 (Tài liệu đã tồn tại trong hệ thống)
    hash_stmt = select(SOPDocument).where(SOPDocument.file_hash == file_hash)
    hash_res = await db.execute(hash_stmt)
    existing_doc = hash_res.scalar_one_or_none()
    if existing_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tài liệu đã tồn tại trong hệ thống (phát hiện trùng lặp mã băm SHA-256 với tài liệu '{existing_doc.document_code}')",
        )

    # 4. Kiểm tra trùng document_code
    code_stmt = select(SOPDocument).where(SOPDocument.document_code == document_code)
    code_res = await db.execute(code_stmt)
    if code_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã tài liệu '{document_code}' đã tồn tại trong hệ thống",
        )

    # 5. Kiểm tra tính hợp lệ của line_id và machine_id nếu được truyền
    if line_id:
        line_stmt = select(ProductionLine).where(ProductionLine.id == line_id)
        line_res = await db.execute(line_stmt)
        if not line_res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy dây chuyền với ID '{line_id}'",
            )

    if machine_id:
        mac_stmt = select(Machine).where(Machine.id == machine_id)
        mac_res = await db.execute(mac_stmt)
        if not mac_res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy thiết bị với ID '{machine_id}'",
            )

    # 6. Xác định số trang PDF
    try:
        reader = pypdf.PdfReader(io.BytesIO(content))
        page_count = len(reader.pages)
    except Exception:
        page_count = 1

    # 7. Lưu file vật lý an toàn vào thư mục UPLOAD_DIR
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_filename = f"{uuid4().hex}_{filename}"
    saved_path = upload_dir / safe_filename
    with open(saved_path, "wb") as f:
        f.write(content)

    # 8. Lưu bản ghi vào CSDL
    doc = SOPDocument(
        document_code=document_code,
        title=title,
        file_name=filename,
        file_path=str(saved_path),
        file_hash=file_hash,
        file_size=len(content),
        version=version,
        page_count=page_count,
        chunk_count=0,
        ingestion_status=IngestionStatus.PENDING,
        line_id=line_id,
        machine_id=machine_id,
        uploaded_by=current_user.id,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


@router.get(
    "/{document_id}/file",
    summary="Tải về hoặc xem luồng nhị phân file PDF (Bảo mật với Bearer token)",
    response_class=FileResponse,
)
async def get_sop_document_file(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SOPDocument).where(SOPDocument.id == document_id)
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy tài liệu SOP với ID '{document_id}'",
        )

    file_path = Path(doc.file_path)
    if not file_path.is_absolute():
        candidate_root = settings.PROJECT_ROOT / file_path
        candidate_backend = settings.BACKEND_DIR / file_path
        if candidate_root.exists():
            file_path = candidate_root
        elif candidate_backend.exists():
            file_path = candidate_backend

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File PDF vật lý không tồn tại trên máy chủ",
        )

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=doc.file_name,
    )


@router.patch(
    "/{document_id}",
    response_model=SOPDocumentResponse,
    summary="Cập nhật thông tin tài liệu SOP (Quản đốc hoặc Admin)",
)
async def update_sop_document(
    document_id: str,
    doc_in: SOPDocumentUpdate,
    current_user: User = Depends(
        require_roles([UserRole.FACTORY_MANAGER, UserRole.ADMIN])
    ),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SOPDocument).where(SOPDocument.id == document_id)
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy tài liệu SOP với ID '{document_id}'",
        )

    update_data = doc_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(doc, field, val)

    await db.commit()
    await db.refresh(doc)
    return doc


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa tài liệu SOP (Chỉ Admin)",
)
async def delete_sop_document(
    document_id: str,
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SOPDocument).where(SOPDocument.id == document_id)
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy tài liệu SOP với ID '{document_id}'",
        )

    # Xóa file vật lý nếu nằm trong thư mục uploads (để tránh rác bộ nhớ)
    try:
        p = Path(doc.file_path)
        if p.exists() and "uploads" in str(p):
            p.unlink()
    except Exception:
        pass

    await db.delete(doc)
    await db.commit()
    return {"message": f"Đã xóa thành công tài liệu SOP '{doc.title}' ({doc.document_code})"}
