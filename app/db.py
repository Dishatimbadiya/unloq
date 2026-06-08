import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from pgvector.sqlalchemy import Vector
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/unloq")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


class PolicyChunk(Base):
    __tablename__ = "policy_chunks"
    id = Column(String, primary_key=True)
    policy_id = Column(String, index=True)
    source = Column(String)
    page = Column(Integer, nullable=True)
    chunk_id = Column(String, unique=True, index=True)
    text = Column(Text)
    embedding = Column(Vector(1536))
    created_at = Column(DateTime, server_default=func.now())


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
