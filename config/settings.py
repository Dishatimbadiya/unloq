"""Configuration and settings using Pydantic."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from .env."""
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/unloq"
    pgvector_dim: int = 1024
    
    # Embeddings
    embedding_model: str = "BAAI/bge-large-en-v1.5"
    
    # Re-ranker
    reranker_model: str = "cross-encoder/msl-mcd6"
    reranker_top_k: int = 3
    
    # Retrieval
    retrieval_top_k: int = 5
    similarity_threshold: float = 0.5
    
    # BM25
    use_bm25_fallback: bool = True
    
    # LLM
    llm_provider: str = "anthropic"  # anthropic | openai
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
