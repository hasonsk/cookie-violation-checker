from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from src.repositories.base import BaseRepository
from src.configs.settings import settings

class CookieFeatureRepository(BaseRepository):
    """Repository for cookie feature operations"""

    def __init__(self):
        super().__init__(settings.db.COOKIE_FEATURES_COLLECTION)

    async def get_features_by_website(self, website_url: str) -> List[Dict[str, Any]]:
        """Get all cookie features for a website"""
        return await self.find_many(
            query={"website_url": website_url},
            sort=[("feature_type", 1), ("name", 1)]
        )

    async def get_features_by_type(self, feature_type: str, limit: int = 0) -> List[Dict[str, Any]]:
        """Get features by type"""
        return await self.find_many(
            query={"feature_type": feature_type},
            limit=limit,
            sort=[("created_at", -1)]
        )
