from typing import Optional
from schemas.policy_schema import PolicyContent
from configs.redis_cache import get_cache, set_cache

class CacheManager:
    """Cache manager cho policy content"""

    async def get_cached_content(self, website_url: str) -> Optional[PolicyContent]:
        key = f"policy_content:{website_url}"
        cached_data = await get_cache(key)
        if cached_data:
            return PolicyContent(**cached_data)
        return None

    async def cache_content(self, website_url: str, content: PolicyContent):
        key = f"policy_content:{website_url}"
        await set_cache(key, content.dict(), ttl=86400)  # TTL: 24h
