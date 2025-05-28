import os
import json
import logging
import redis.asyncio as redis

logger = logging.getLogger(__name__)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Kết nối Redis
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def set_cache(key: str, value: dict, ttl: int = 3600):
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
