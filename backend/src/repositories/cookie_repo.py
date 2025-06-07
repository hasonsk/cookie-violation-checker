from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from repositories.base_repository import BaseRepository
from configs.app_settings import COOKIE_FEATURES_COLLECTION

class CookieFeatureRepository(BaseRepository):
    """Repository for cookie feature operations"""

    def __init__(self):
        super().__init__(COOKIE_FEATURES_COLLECTION)

    async def create_cookie_feature(self, document: Dict[str, Any]) -> str:
        """Create a new cookie feature record"""
        return await self.insert_one(document)

    async def get_features_by_website(self, website_url: str) -> List[Dict[str, Any]]:
        """Get all cookie features for a website"""
        return await self.find_many(
            query={"website_url": website_url},
            sort=[("feature_type", 1), ("name", 1)]
        )

    async def get_specific_features(self, website_url: str) -> List[Dict[str, Any]]:
        """Get specific cookie features for a website"""
        return await self.find_many(
            query={"website_url": website_url, "feature_type": "specific"},
            sort=[("name", 1)]
        )

    async def get_general_features(self, website_url: str) -> List[Dict[str, Any]]:
        """Get general cookie features for a website"""
        return await self.find_many(
            query={"website_url": website_url, "feature_type": "general"},
            sort=[("purpose", 1)]
        )

    async def get_feature_by_name(self, website_url: str, cookie_name: str) -> Optional[Dict[str, Any]]:
        """Get specific cookie feature by name"""
        return await self.find_one({
            "website_url": website_url,
            "name": cookie_name,
            "feature_type": "specific"
        })

    async def get_features_by_type(self, feature_type: str, limit: int = 0) -> List[Dict[str, Any]]:
        """Get features by type"""
        return await self.find_many(
            query={"feature_type": feature_type},
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def update_feature(self, website_url: str, name: str, update_fields: Dict[str, Any]) -> int:
        """Update a cookie feature"""
        return await self.update_one(
            {"website_url": website_url, "name": name},
            update_fields
        )

    async def delete_features_by_website(self, website_url: str) -> int:
        """Delete all features for a website"""
        return await self.delete_many({"website_url": website_url})
