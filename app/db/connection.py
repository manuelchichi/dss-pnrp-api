import os
from pymongo import AsyncMongoClient

db_client: AsyncMongoClient | None = None

async def connect_db() -> None:
    """Create database connection."""
    global db_client

    mongodb_url = os.environ.get("MONGODB_URL")
    if not mongodb_url:
        raise RuntimeError("MONGODB_URL environment variable not set")
    db_client = AsyncMongoClient(mongodb_url)
    print("📦 Connected to MongoDB")


async def close_db() -> None:
    """Close database connection."""
    global db_client
    if db_client:
        db_client.close()
        print("🔌 MongoDB connection closed")


async def get_db_client():
    global db_client
    if db_client is None:
        raise RuntimeError("Database client is not initialized. Did you call connect_db()?")

    return db_client
