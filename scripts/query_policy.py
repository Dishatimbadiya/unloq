#!/usr/bin/env python
"""Script to query the Policy Assistant."""
import asyncio
import sys
import json
from config import settings
from src.unloq_rag.retrieval import EmbeddingService, ReRanker, BM25Search, knn_query
from src.unloq_rag.orchestration import PolicyAssistant


async def main():
    if len(sys.argv) < 2:
        print("Usage: python query_policy.py '<question>'")
        print("Example: python query_policy.py 'What is the travel limit?'")
        sys.exit(1)
    
    question = sys.argv[1]
    
    try:
        # Initialize components
        print("Initializing RAG components...")
        emb = EmbeddingService(settings.embedding_model)
        reranker = ReRanker(settings.reranker_model)
        bm25 = BM25Search()
        
        assistant = PolicyAssistant(
            embedding_service=emb,
            reranker=reranker,
            bm25=bm25,
            similarity_threshold=settings.similarity_threshold
        )
        print("✓ Components initialized\n")
        
        # Query
        print(f"Question: {question}\n")
        result = await assistant.answer(question)
        
        print(f"Answer: {result.answer}")
        print(f"Confidence: {result.confidence}")
        if result.citations:
            print(f"Citations: {', '.join([c['policy_id'] for c in result.citations])}")
        if result.answer_trace:
            print(f"Trace: {result.answer_trace}")
    
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
