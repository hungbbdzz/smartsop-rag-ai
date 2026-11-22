"""
RAG Ingestion, Retrieval, Prompting, Citations, Dual-LLM & Streaming package for SmartSOP AI.
"""

from app.rag.citations import (
    CITATION_PATTERN,
    extract_verified_citations,
    strip_unverified_citations,
)
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
from app.rag.llm import (
    BaseLLMProvider,
    GeminiProvider,
    OllamaProvider,
    create_llm_provider,
    get_llm_provider,
)
from app.rag.prompt_engine import (
    REFUSAL_MESSAGE,
    SYSTEM_PROMPT,
    build_rag_prompt,
    format_context_blocks,
)
from app.rag.retriever import (
    SOPRetriever,
    extract_error_codes,
    get_retriever,
)
from app.rag.streaming import format_sse_event, stream_rag_response
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
    "SOPRetriever",
    "extract_error_codes",
    "get_retriever",
    "REFUSAL_MESSAGE",
    "SYSTEM_PROMPT",
    "format_context_blocks",
    "build_rag_prompt",
    "CITATION_PATTERN",
    "extract_verified_citations",
    "strip_unverified_citations",
    "BaseLLMProvider",
    "GeminiProvider",
    "OllamaProvider",
    "create_llm_provider",
    "get_llm_provider",
    "format_sse_event",
    "stream_rag_response",
]
