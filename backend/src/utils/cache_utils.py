from typing import Optional
import json
import redis.asyncio as redis
from loguru import logger

from src.schemas.policy import PolicyContent
from src.configs.settings import settings

redis_client = redis.from_url(settings.redis.REDIS_URL, decode_responses=True)

async def set_cache(key: str, value: dict, ttl: int = settings.redis.REDIS_TTL):
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

class CacheManager:
    async def get_cached_content(self, website_url: str) -> Optional[PolicyContent]:
        key = f"policy_content:{website_url}"
        cached_data = await get_cache(key)
        if cached_data:
            return PolicyContent(**cached_data)
        return None

    async def cache_content(self, website_url: str, content: PolicyContent):
        key = f"policy_content:{website_url}"
        await set_cache(key, content.dict(), ttl=settings.redis.REDIS_TTL)
