from typing import Optional
from schemas.policy_schema import PolicyContent
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Cache management utility"""

    async def get_cached_content(self, website_url: str) -> Optional[PolicyContent]:
        """Get cached policy content"""
        try:
            # Uncomment when redis_cache is available
            # cache_key = f"policy_content:{website_url}"
            # cached_data = await redis_cache.get(cache_key, as_json=True)
            # if cached_data:
            #     return PolicyContent(**cached_data)
            return None
        except Exception as e:
            logger.error(f"Error getting cached content: {e}")
            return None

    async def cache_content(self, website_url: str, content: PolicyContent):
        """Cache policy content"""
        try:
            # Uncomment when redis_cache is available
            # cache_key = f"policy_content:{website_url}"
            # cache_data = {
            #     'website_url': content.website_url,
            #     'policy_url': content.policy_url,
            #     'original_content': content.original_content,
            #     'translated_content': content.translated_content,
            #     'detected_language': content.detected_language,
            #     'table_content': [table for table in content.table_content],
            #     'translated_table_content': content.translated_table_content,
            #     'error': content.error
            # }
            # await redis_cache.set(cache_key, cache_data, ttl=3600 * 24)
            pass
        except Exception as e:
            logger.error(f"Error caching content: {e}")
