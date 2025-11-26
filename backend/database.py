import os
import asyncpg
from typing import Optional

# Global pool variable
db_pool: Optional[asyncpg.Pool] = None

def get_db_url():
    return os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/uns_visa")

async def init_db():
    """Initialize database pool"""
    global db_pool
    if not db_pool:
        db_pool = await asyncpg.create_pool(get_db_url())

async def close_db():
    """Close database pool"""
    global db_pool
    if db_pool:
        await db_pool.close()

async def get_db_pool() -> asyncpg.Pool:
    """Get the database pool"""
    global db_pool
    if not db_pool:
        await init_db()
    return db_pool
