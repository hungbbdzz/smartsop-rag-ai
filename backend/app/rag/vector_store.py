import logging
from pathlib import Path
import threading
from typing import Any, Dict, List, Optional, Union

import chromadb

from app.core.config import settings
from app.rag.embeddings import ChromaEmbeddingFunction

logger = logging.getLogger("smartsop.rag.vector_store")

_vector_store_lock = threading.Lock()
_vector_store_instance: Optional["VectorStoreService"] = None


class VectorStoreService:
    """
    Dịch vụ lưu trữ và truy vấn vector cục bộ sử dụng ChromaDB PersistentClient.
    Mặc định sử dụng collection 'sop_documents' với độ đo Cosine Similarity.
    """

    def __init__(
        self,
        persist_dir: Optional[Union[str, Path]] = None,
        collection_name: str = "sop_documents",
        embedding_function: Optional[Any] = None,
    ) -> None:
        self.persist_dir = Path(persist_dir or settings.CHROMA_PERSIST_DIR)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self.embedding_function = embedding_function or ChromaEmbeddingFunction()

        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
            embedding_function=self.embedding_function,
        )

    def upsert_chunks(
        self,
        doc_id: str,
        chunks: List[Dict[str, Any]],
        source_file: str,
        doc_code: str = "",
    ) -> List[str]:
        """
        Nạp danh sách các đoạn phân đoạn vào ChromaDB với ID tất định `{doc_id}:{page_num}:{chunk_index}`.
        Trả về danh sách chroma_id đã được lưu.
        """
        if not chunks:
            return []

        ids: List[str] = []
        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []

        for chunk in chunks:
            page_num = int(chunk["page_number"])
            chunk_idx = int(chunk["chunk_index"])
            chroma_id = f"{doc_id}:{page_num}:{chunk_idx}"

            ids.append(chroma_id)
            documents.append(chunk["content"])
            metadatas.append({
                "doc_id": doc_id,
                "doc_code": doc_code,
                "page_num": page_num,
                "chunk_index": chunk_idx,
                "source_file": source_file,
                "section_title": str(chunk.get("section_title") or "")[:255],
                "is_table": bool(chunk.get("is_table", False)),
            })

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )
        return ids

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Truy vấn tương đồng Cosine trả về danh sách kết quả sắp xếp theo score giảm dần.
        """
        if not query_text or not query_text.strip():
            return []

        total = self.count()
        if total == 0:
            return []

        n_results = min(top_k, total)
        raw = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        raw_ids = (raw.get("ids") or [[]])[0]
        raw_docs = (raw.get("documents") or [[]])[0]
        raw_metas = (raw.get("metadatas") or [[]])[0]
        raw_dists = (raw.get("distances") or [[]])[0]

        results: List[Dict[str, Any]] = []
        for chroma_id, content, meta, dist in zip(raw_ids, raw_docs, raw_metas, raw_dists):
            score = round(1.0 - float(dist), 4)
            results.append({
                "chroma_id": chroma_id,
                "content": content,
                "score": score,
                "metadata": meta or {},
            })

        results.sort(key=lambda item: item["score"], reverse=True)
        return results

    def delete_by_doc_id(self, doc_id: str) -> int:
        """Xóa toàn bộ vector thuộc tài liệu có `doc_id` trong ChromaDB."""
        existing = self.collection.get(where={"doc_id": doc_id}, include=[])
        ids = existing.get("ids") or []
        if ids:
            self.collection.delete(ids=ids)
        return len(ids)

    def count(self) -> int:
        """Tổng số vector đang lưu trong collection."""
        return self.collection.count()

    def count_by_doc_id(self, doc_id: str) -> int:
        """Đếm số vector hiện có của một tài liệu theo `doc_id`."""
        existing = self.collection.get(where={"doc_id": doc_id}, include=[])
        return len(existing.get("ids") or [])


def get_vector_store() -> VectorStoreService:
    """Trả về instance Singleton duy nhất của VectorStoreService."""
    global _vector_store_instance
    if _vector_store_instance is None:
        with _vector_store_lock:
            if _vector_store_instance is None:
                _vector_store_instance = VectorStoreService()
    return _vector_store_instance
