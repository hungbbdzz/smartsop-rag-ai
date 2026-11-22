import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers.auth import router as auth_router
from app.routers.production_lines import router as production_lines_router
from app.routers.machines import router as machines_router
from app.routers.users import router as users_router
from app.routers.incident_tickets import router as incident_tickets_router
from app.routers.sop_documents import router as sop_documents_router
from app.routers.chat import router as chat_router

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("smartsop")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Quản lý vòng đời ứng dụng (Lifespan):
    1. Khởi động: Tạo thư mục lưu trữ, kiểm tra kết nối CSDL
    2. Tắt: Giải phóng tài nguyên
    """
    logger.info("🚀 Khởi động SmartSOP AI Backend Service...")
    
    # Tạo các thư mục lưu trữ nếu chưa có
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)
    Path("./data").mkdir(parents=True, exist_ok=True)
    
    logger.info(f"📁 Thư mục Uploads: {settings.UPLOAD_DIR}")
    logger.info(f"📁 Thư mục ChromaDB: {settings.CHROMA_PERSIST_DIR}")
    logger.info(f"🗄️ CSDL: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")

    yield

    logger.info("🛑 Dừng SmartSOP AI Backend Service...")


# Khởi tạo FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Hệ thống Web Quản lý và Tra cứu Quy trình Vận hành Chuẩn (SOP) Nhà máy Tích hợp Trợ lý RAG AI",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health Check"])
async def health_check():
    """Endpoint kiểm tra trạng thái hoạt động của hệ thống (Liveness & Readiness probe)."""
    return {
        "status": "ok",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Chào mừng bạn đến với {settings.PROJECT_NAME} API Service!",
        "docs": "/docs",
        "health": "/health",
    }


# Gắn các API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(production_lines_router, prefix=settings.API_V1_STR)
app.include_router(machines_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(incident_tickets_router, prefix=settings.API_V1_STR)
app.include_router(sop_documents_router, prefix=settings.API_V1_STR)
app.include_router(chat_router, prefix=settings.API_V1_STR)

