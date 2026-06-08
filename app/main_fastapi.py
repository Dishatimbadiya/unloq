from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging
from .ingest import chunk_text
from .embeddings import EmbeddingService
from .reranker import ReRanker
from .bm25_search import BM25Search
from .store import upsert_chunks
from .db import init_db
from .orchestrator import PolicyAssistant
from .types import DocumentChunk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Unloq Policy Assistant (v1) — Production RAG")

# Global components (initialize on startup)
embedding_service: Optional[EmbeddingService] = None
reranker: Optional[ReRanker] = None
bm25_search: Optional[BM25Search] = None
assistant: Optional[PolicyAssistant] = None


class IngestRequest(BaseModel):
    policy_id: str
    source: str
    text: str


class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5


@app.on_event("startup")
async def startup():
    """Initialize DB and RAG components."""
    global embedding_service, reranker, bm25_search, assistant
    
    try:
        await init_db()
        logger.info("DB initialized")
    except Exception as e:
        logger.error(f"DB init failed: {e}")
    
    try:
        embedding_service = EmbeddingService()
        logger.info("Embedding service initialized (BAAI/bge-large-en-v1.5)")
    except Exception as e:
        logger.warn(f"Embedding service init failed (using stub): {e}")
        embedding_service = None
    
    try:
        reranker = ReRanker()
        logger.info("Re-ranker initialized (Cross Encoder MiniLM)")
    except Exception as e:
        logger.warn(f"Re-ranker init failed: {e}")
        reranker = None
    
    bm25_search = BM25Search()
    logger.info("BM25 search initialized")
    
    assistant = PolicyAssistant(
        embedding_service=embedding_service,
        reranker=reranker,
        bm25=bm25_search
    )
    logger.info("Policy Assistant ready")


@app.post("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "embeddings": embedding_service is not None,
        "reranker": reranker is not None,
        "bm25": bm25_search is not None
    }


@app.post("/ingest")
async def ingest(req: IngestRequest):
    """Ingest policy text: chunk → embed → store."""
    try:
        # Chunk the text
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
            logger.info(f"Embedded {len(chunks)} chunks")
        else:
            # Fallback: mock embeddings
            for i, c in enumerate(chunks):
                c.embedding = [0.0] * 1024
            logger.warn("Using mock embeddings (service not initialized)")
        
        # Store in DB
        await upsert_chunks(chunks)
        
        # Index in BM25
        if bm25_search:
            bm25_search.index(chunks)
        
        return {
            "status": "ok",
            "policy_id": req.policy_id,
            "ingested_chunks": len(chunks)
        }
    
    except Exception as e:
        logger.error(f"Ingest failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
async def query(req: QueryRequest):
    """Query: retrieve + rerank + generate."""
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
