from pathlib import Path
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Đường dẫn thư mục gốc hệ thống
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartSOP AI Factory Assistant"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Thư mục hệ thống cố định (không phụ thuộc working directory)
    BACKEND_DIR: Path = BACKEND_DIR
    PROJECT_ROOT: Path = PROJECT_ROOT
    DATA_DIR: Path = BACKEND_DIR / "data"
    SOPS_SAMPLE_DIR: Path = PROJECT_ROOT / "data" / "sops"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/smartsop.db"

    # JWT Security
    SECRET_KEY: str = "smartsop-dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours (1 ca sản xuất)

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    # Storage paths
    UPLOAD_DIR: str = str(BACKEND_DIR / "data" / "uploads")
    CHROMA_PERSIST_DIR: str = str(BACKEND_DIR / "data" / "chromadb")

    # AI & LLM Settings
    LLM_PROVIDER: str = "gemini"  # "gemini" | "ollama"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b"
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-m3"
    SIMILARITY_THRESHOLD: float = 0.65

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        """Chuẩn hóa đường dẫn file SQLite về tuyệt đối để không bị phụ thuộc CWD."""
        if v and "sqlite" in v and "./data/" in v:
            db_file = (BACKEND_DIR / "data" / "smartsop.db").resolve().as_posix()
            return f"sqlite+aiosqlite:///{db_file}"
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
