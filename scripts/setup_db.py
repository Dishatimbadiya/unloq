#!/usr/bin/env python
"""Script to initialize the database schema."""
import asyncio
from src.unloq_rag.storage import init_db


async def main():
    try:
        print("Initializing database...")
        await init_db()
        print("✓ Database schema created successfully")
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
