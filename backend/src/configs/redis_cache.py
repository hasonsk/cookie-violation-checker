import os
import json
from loguru import logger
import redis.asyncio as redis
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
REDIS_TTL = int(os.environ.get("REDIS_TTL", "3600"))

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def set_cache(key: str, value: dict, ttl: int = REDIS_TTL):
    """Lưu cache với TTL (giây)"""
    try:
        await redis_client.set(key, json.dumps(value), ex=ttl)
    except Exception as e:
        logger.error(f"Redis set_cache error: {e}")

async def get_cache(key: str) -> dict:
    """Lấy cache (nếu có)"""
    try:
        cached = await redis_client.get(key)
        return json.loads(cached) if cached else None
    except Exception as e:
        logger.error(f"Redis get_cache error: {e}")
        return None
