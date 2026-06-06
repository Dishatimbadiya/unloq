"""FastAPI application for Policy Assistant."""
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from config import settings
from src.unloq_rag.ingestion import chunk_text
from src.unloq_rag.retrieval import EmbeddingService, ReRanker, BM25Search, upsert_chunks
from src.unloq_rag.orchestration import PolicyAssistant
from src.unloq_rag.storage import init_db

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Unloq Policy Assistant (v1)",
    description="Production-grade RAG system for policy Q&A",
    version="1.0.0"
)

# Global components (initialize on startup)
embedding_service: Optional[EmbeddingService] = None
reranker: Optional[ReRanker] = None
bm25_search: Optional[BM25Search] = None
assistant: Optional[PolicyAssistant] = None


class IngestRequest(BaseModel):
    """Request to ingest a policy."""
    policy_id: str
    source: str
    text: str


class QueryRequest(BaseModel):
    """Request to query the assistant."""
    question: str
    top_k: Optional[int] = 5


@app.on_event("startup")
async def startup():
    """Initialize DB and RAG components."""
    global embedding_service, reranker, bm25_search, assistant
    
    try:
        await init_db()
        logger.info("✓ Database initialized")
    except Exception as e:
        logger.error(f"✗ DB init failed: {e}")
    
    try:
        embedding_service = EmbeddingService(settings.embedding_model)
        logger.info(f"✓ Embedding service initialized ({settings.embedding_model})")
    except Exception as e:
        logger.warning(f"✗ Embedding service init failed: {e}")
        embedding_service = None
    
    try:
        reranker = ReRanker(settings.reranker_model)
        logger.info(f"✓ Re-ranker initialized ({settings.reranker_model})")
    except Exception as e:
        logger.warning(f"✗ Re-ranker init failed: {e}")
        reranker = None
    
    bm25_search = BM25Search()
    logger.info("✓ BM25 search initialized")
    
    assistant = PolicyAssistant(
        embedding_service=embedding_service,
        reranker=reranker,
        bm25=bm25_search,
        similarity_threshold=settings.similarity_threshold
    )
    logger.info("✓ Policy Assistant ready")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "components": {
            "embeddings": embedding_service is not None,
            "reranker": reranker is not None,
            "bm25": bm25_search is not None,
            "assistant": assistant is not None
        }
    }


@app.post("/ingest")
async def ingest(req: IngestRequest):
    """Ingest policy: chunk → embed → store."""
    try:
        # Chunk text
        chunks = chunk_text(
            req.text,
            policy_id=req.policy_id,
            source=req.source,
            chunk_size=500
        )
        
        # Embed chunks
        if embedding_service:
            texts = [c.text for c in chunks]
            embeddings = embedding_service.embed_texts(texts)
            for c, emb in zip(chunks, embeddings):
                c.embedding = emb
            logger.info(f"Embedded {len(chunks)} chunks for {req.policy_id}")
        else:
            # Fallback: mock embeddings
            for i, c in enumerate(chunks):
                c.embedding = [0.0] * settings.pgvector_dim
            logger.warning(f"Using mock embeddings for {req.policy_id}")
        
        # Store in DB
        await upsert_chunks(chunks)
        
        # Index in BM25
        if bm25_search:
            bm25_search.index(chunks)
        
        return {
            "status": "ok",
            "policy_id": req.policy_id,
            "ingested_chunks": len(chunks),
            "total_text_chars": len(req.text)
        }
    
    except Exception as e:
        logger.error(f"Ingest failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
async def query(req: QueryRequest):
    """Query: retrieve + rank + generate."""
    try:
        if not assistant:
            raise HTTPException(status_code=500, detail="Assistant not initialized")
        
        result = await assistant.answer(req.question)
        
        return {
            "answer": result.answer,
            "citations": result.citations,
            "confidence": result.confidence,
            "conflict": result.conflict,
            "answer_trace": result.answer_trace
        }
    
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
