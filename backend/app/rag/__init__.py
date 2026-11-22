"""
RAG Ingestion, Retrieval, Prompting, Citations & Dual-LLM package for SmartSOP AI:
- embeddings: Lazy Singleton BAAI/bge-m3 wrapper & ChromaEmbeddingFunction
- vector_store: Singleton ChromaDB PersistentClient service (cosine space)
- ingestion: Bounded-concurrency background worker syncing PDF chunks to ChromaDB & SQL DB
- retriever: Dual-retrieval (error-code regex boost + cosine search) with similarity gating
- prompt_engine: Anti-hallucination hard guardrails system prompt & context formatter
- citations: Grounded citation verifier & hallucinated-tag stripper
- llm: Dual-provider LLM abstraction (Gemini API & Ollama local) with async streaming
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
]
