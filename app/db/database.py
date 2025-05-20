from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings  # type: ignore
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the .env file")

# Make sure DATABASE_URL uses 'postgresql+asyncpg'
if not DATABASE_URL.startswith("postgresql+asyncpg"):
    raise ValueError("DATABASE_URL must start with 'postgresql+asyncpg' for async support.")

# Create the async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create sessionmaker for async sessions
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# Declare the base
Base = declarative_base()

# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
