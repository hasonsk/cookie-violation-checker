from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from src.repositories.base import BaseRepository
from src.configs.settings import settings

class ViolationRepository(BaseRepository):
    """Repository for violation operations"""

    def __init__(self):
        super().__init__(settings.db.VIOLATIONS_COLLECTION) # Assuming "violations" is the collection name

    async def create_violation(self, document: Dict[str, Any]) -> str:
        """Create a new violation record"""
        return await self.insert_one(document)

    async def get_violations_by_website(self, website_url: str) -> List[Dict[str, Any]]:
        """Get all violations for a website"""
        return await self.find_many(
            query={"website_url": website_url},
            sort=[("severity", 1), ("violation_type", 1), ("cookie_name", 1)]
        )

    async def get_recent_violations(self, hours_ago: int = 24, limit: int = 0) -> List[Dict[str, Any]]:
        """Get recent violations within specified hours"""
        time_threshold = datetime.utcnow() - timedelta(hours=hours_ago)
        return await self.find_many(
            query={"created_at": {"$gte": time_threshold}},
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def delete_violations_by_website(self, website_url: str) -> int:
        """Delete all violations for a website"""
        return await self.delete_many({"website_url": website_url})
