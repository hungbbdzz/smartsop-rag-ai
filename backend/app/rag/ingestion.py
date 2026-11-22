import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fastapi.concurrency import run_in_threadpool
from sqlalchemy import delete, select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.sop_chunk import SOPChunk
from app.models.sop_document import IngestionStatus, SOPDocument
from app.rag.vector_store import VectorStoreService, get_vector_store
from app.utils.chunker import chunk_document
from app.utils.pdf_parser import parse_pdf_document

logger = logging.getLogger("smartsop.rag.ingestion")

# Giới hạn số tài liệu được bóc tách & nạp vector đồng thời để tránh tràn RAM
INGESTION_SEMAPHORE = asyncio.Semaphore(2)


def _resolve_pdf_path(file_path_str: str) -> Path:
    """Chuẩn hóa đường dẫn tệp PDF từ đường dẫn tuyệt đối hoặc tương đối trong project."""
    file_path = Path(file_path_str)
    if file_path.is_absolute():
        return file_path

    candidate_root = settings.PROJECT_ROOT / file_path
    if candidate_root.exists():
        return candidate_root

    candidate_backend = settings.BACKEND_DIR / file_path
    if candidate_backend.exists():
        return candidate_backend

    return file_path


def _parse_and_chunk_sync(pdf_path: Path) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Tác vụ nặng CPU: bóc tách PDF và phân đoạn Table-Aware trong threadpool."""
    parsed_doc = parse_pdf_document(pdf_path)
    chunks = chunk_document(parsed_doc)
    return parsed_doc, chunks


async def ingest_sop_document(
    document_id: str,
    vector_store: Optional[VectorStoreService] = None,
    session_factory: Any = None,
) -> Dict[str, Any]:
    """
    Background worker thực hiện pipeline nạp tri thức cho 1 tài liệu SOP:
    1. Chuyển trạng thái PROCESSING trong CSDL quan hệ.
    2. Bóc tách PDF + Table-Aware Chunking trong threadpool.
    3. Xóa vector cũ (nếu có) và upsert vector mới vào ChromaDB với ID tất định.
    4. Đồng bộ bảng đối soát `sop_chunks` và cập nhật trạng thái COMPLETED.
    """
    factory = session_factory or AsyncSessionLocal

    async with INGESTION_SEMAPHORE:
        async with factory() as db:
            result = await db.execute(select(SOPDocument).where(SOPDocument.id == document_id))
            doc = result.scalar_one_or_none()
            if not doc:
                raise ValueError(f"Không tìm thấy tài liệu SOP với ID '{document_id}'")

            file_path_str = doc.file_path
            file_name = doc.file_name
            doc_code = doc.document_code

            doc.ingestion_status = IngestionStatus.PROCESSING
            doc.ingestion_error = None
            await db.commit()

        try:
            pdf_path = _resolve_pdf_path(file_path_str)
            if not pdf_path.exists():
                raise FileNotFoundError(f"Không tìm thấy tệp PDF vật lý tại: {pdf_path}")

            parsed_doc, chunks = await run_in_threadpool(_parse_and_chunk_sync, pdf_path)

            vs = vector_store or get_vector_store()
            await run_in_threadpool(vs.delete_by_doc_id, document_id)
            chroma_ids = await run_in_threadpool(
                vs.upsert_chunks,
                document_id,
                chunks,
                file_name,
                doc_code,
            )

            async with factory() as db:
                await db.execute(delete(SOPChunk).where(SOPChunk.document_id == document_id))
                for chunk, chroma_id in zip(chunks, chroma_ids):
                    section_title = str(chunk.get("section_title") or "")[:255] or None
                    db.add(
                        SOPChunk(
                            document_id=document_id,
                            chroma_id=chroma_id,
                            page_num=int(chunk["page_number"]),
                            chunk_index=int(chunk["chunk_index"]),
                            section_title=section_title,
                            char_count=int(chunk["char_count"]),
                        )
                    )

                res = await db.execute(select(SOPDocument).where(SOPDocument.id == document_id))
                doc = res.scalar_one_or_none()
                if doc:
                    doc.page_count = int(parsed_doc.get("total_pages", doc.page_count))
                    doc.chunk_count = len(chunks)
                    doc.ingestion_status = IngestionStatus.COMPLETED
                    doc.ingestion_error = None
                    await db.commit()

            logger.info(
                f"Đã nạp thành công tài liệu '{doc_code}' ({document_id}): "
                f"{len(chunks)} chunks vào ChromaDB."
            )
            return {
                "document_id": document_id,
                "status": IngestionStatus.COMPLETED.value,
                "page_count": int(parsed_doc.get("total_pages", 0)),
                "chunk_count": len(chunks),
                "chroma_ids": chroma_ids,
            }

        except Exception as exc:
            logger.exception(f"Lỗi nạp vector tài liệu SOP '{document_id}': {exc}")
            async with factory() as db:
                res = await db.execute(select(SOPDocument).where(SOPDocument.id == document_id))
                doc = res.scalar_one_or_none()
                if doc:
                    doc.ingestion_status = IngestionStatus.FAILED
                    doc.ingestion_error = str(exc)[:500]
                    await db.commit()
            raise


async def delete_sop_vectors(
    document_id: str,
    vector_store: Optional[VectorStoreService] = None,
) -> int:
    """Xóa đồng bộ toàn bộ vector của tài liệu SOP khỏi ChromaDB trong threadpool."""
    vs = vector_store or get_vector_store()
    deleted_count = await run_in_threadpool(vs.delete_by_doc_id, document_id)
    logger.info(f"Đã xóa {deleted_count} vectors khỏi ChromaDB cho document_id='{document_id}'.")
    return deleted_count
