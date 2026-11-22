import logging
import threading
from typing import Any, Callable, Dict, List, Optional

from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

from app.core.config import settings

logger = logging.getLogger("smartsop.rag.embeddings")

_embedding_service_lock = threading.Lock()
_embedding_service_instance: Optional["EmbeddingService"] = None


class EmbeddingService:
    """
    Singleton quản lý mô hình embedding đa ngữ BAAI/bge-m3 (1024 chiều).
    Mô hình chỉ được nạp vào RAM ở lần gọi encode() đầu tiên (Lazy Initialization)
    để tránh tốn thời gian khởi động khi không cần đến.
    """

    def __init__(self, model_name: Optional[str] = None) -> None:
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self._model: Optional[Any] = None
        self._model_lock = threading.Lock()

    def _get_model(self) -> Any:
        if self._model is None:
            with self._model_lock:
                if self._model is None:
                    logger.info(f"Đang nạp mô hình embedding '{self.model_name}'...")
                    from sentence_transformers import SentenceTransformer

                    self._model = SentenceTransformer(self.model_name)
                    logger.info(f"Đã nạp xong mô hình embedding '{self.model_name}'.")
        return self._model

    def encode(self, texts: List[str]) -> List[List[float]]:
        """Mã hóa danh sách văn bản thành vector chuẩn hóa L2 (dạng list float)."""
        if not texts:
            return []
        model = self._get_model()
        vectors = model.encode(texts, normalize_embeddings=True)
        return [vec.tolist() for vec in vectors]


def get_embedding_service() -> EmbeddingService:
    """Trả về instance Singleton duy nhất của EmbeddingService."""
    global _embedding_service_instance
    if _embedding_service_instance is None:
        with _embedding_service_lock:
            if _embedding_service_instance is None:
                _embedding_service_instance = EmbeddingService()
    return _embedding_service_instance


class ChromaEmbeddingFunction(EmbeddingFunction[Documents]):
    """
    Adapter EmbeddingFunction tương thích ChromaDB 1.x.
    Cho phép truyền encode_fn tùy chỉnh trong kiểm thử hoặc dùng mặc định BAAI/bge-m3.
    """

    def __init__(
        self,
        encode_fn: Optional[Callable[[List[str]], List[List[float]]]] = None,
        model_name: Optional[str] = None,
    ) -> None:
        self._model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self._encode_fn = encode_fn

    def __call__(self, input: Documents) -> Embeddings:
        texts = list(input)
        if not texts:
            return []
        encoder = self._encode_fn or get_embedding_service().encode
        return encoder(texts)  # type: ignore[return-value]

    @staticmethod
    def name() -> str:
        return "smartsop-bge-m3"

    def default_space(self) -> str:
        return "cosine"

    def supported_spaces(self) -> List[str]:
        return ["cosine", "l2", "ip"]

    def get_config(self) -> Dict[str, Any]:
        return {"model_name": self._model_name}

    @staticmethod
    def build_from_config(config: Dict[str, Any]) -> "ChromaEmbeddingFunction":
        return ChromaEmbeddingFunction(model_name=config.get("model_name"))
