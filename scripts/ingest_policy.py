#!/usr/bin/env python
"""Script to ingest a policy PDF into the system."""
import asyncio
import sys
from pathlib import Path
from src.unloq_rag.ingestion import extract_full_text, chunk_text
from src.unloq_rag.retrieval import EmbeddingService, upsert_chunks
from src.unloq_rag.storage import init_db


async def main():
    if len(sys.argv) < 3:
        print("Usage: python ingest_policy.py <pdf_path> <policy_id>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    policy_id = sys.argv[2]
    
    if not Path(pdf_path).exists():
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)
    
    try:
        # Initialize DB
        await init_db()
        print(f"✓ Database initialized")
        
        # Extract text
        text = extract_full_text(pdf_path)
        print(f"✓ Extracted {len(text)} characters from {pdf_path}")
        
        # Chunk
        chunks = chunk_text(text, policy_id=policy_id, source=Path(pdf_path).name)
        print(f"✓ Created {len(chunks)} chunks")
        
        # Embed
        emb_service = EmbeddingService()
        texts = [c.text for c in chunks]
        embeddings = emb_service.embed_texts(texts)
        for c, emb in zip(chunks, embeddings):
            c.embedding = emb
        print(f"✓ Embedded all chunks")
        
        # Store
        await upsert_chunks(chunks)
        print(f"✓ Stored {len(chunks)} chunks in database")
        print(f"✓ Policy {policy_id} ingested successfully")
    
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
