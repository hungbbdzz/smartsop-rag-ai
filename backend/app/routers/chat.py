from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.rag.streaming import stream_rag_response
from app.schemas.chat import ChatQueryRequest

router = APIRouter(
    prefix="/chat",
    tags=["RAG Assistant Chat"],
)


@router.post(
    "/query",
    summary="Hỏi đáp Trợ lý Kỹ thuật SOP qua Server-Sent Events (SSE Streaming)",
)
async def chat_query_sse(
    request: Request,
    query_in: ChatQueryRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Nhận câu hỏi kỹ thuật, truy hồi ngữ cảnh SOP và truyền luồng token + nguồn trích dẫn
    theo thời gian thực qua giao thức `text/event-stream`.
    """
    return StreamingResponse(
        stream_rag_response(
            request=request,
            query_in=query_in,
            user_id=current_user.id,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
