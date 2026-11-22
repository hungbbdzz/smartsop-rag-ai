"""
RAG Ingestion & Vector Store package for SmartSOP AI:
- embeddings: Lazy Singleton BAAI/bge-m3 wrapper & ChromaEmbeddingFunction
- vector_store: Singleton ChromaDB PersistentClient service (cosine space)
- ingestion: Bounded-concurrency background worker syncing PDF chunks to ChromaDB & SQL DB
"""

from app.rag.embeddings import (
    ChromaEmbeddingFunction,
    EmbeddingService,
    get_embedding_service,
)
from app.rag.ingestion import (
    INGESTION_SEMAPHORE,
    delete_sop_vectors,
    ingest_sop_document,
)
from app.rag.vector_store import VectorStoreService, get_vector_store

__all__ = [
    "EmbeddingService",
    "ChromaEmbeddingFunction",
    "get_embedding_service",
    "VectorStoreService",
    "get_vector_store",
    "INGESTION_SEMAPHORE",
    "ingest_sop_document",
    "delete_sop_vectors",
]
