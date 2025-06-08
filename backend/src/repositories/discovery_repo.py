from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from src.repositories.base_repository import BaseRepository
from src.configs.settings import settings

class PolicyDiscoveryRepository(BaseRepository):
    def __init__(self):
        super().__init__(settings.db.POLICY_DISCOVERY_COLLECTION)

    async def create_discovery_result(self, document: Dict[str, Any]) -> str:
        """Create a new policy discovery result"""
        return await self.insert_one(document)

    async def get_by_website_url(self, website_url: str) -> Optional[Dict[str, Any]]:
        """Get policy discovery by website URL"""
        return await self.find_one({"website_url": website_url})

    async def get_latest_by_website_url(self, website_url: str) -> Optional[Dict[str, Any]]:
        """Get latest policy discovery for a website"""
        results = await self.find_many(
            query={"website_url": website_url},
            limit=1,
            sort=[("created_at", -1)]
        )
        return results[0] if results else None

    async def get_successful_discoveries(self, limit: int = 0) -> List[Dict[str, Any]]:
        """Get all successful policy discoveries"""
        return await self.find_many(
            query={"policy_url": {"$ne": None}, "error": None},
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def get_failed_discoveries(self, limit: int = 0) -> List[Dict[str, Any]]:
        """Get all failed policy discoveries"""
        return await self.find_many(
            query={"$or": [{"policy_url": None}, {"error": {"$ne": None}}]},
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def get_by_discovery_method(self, method: str, limit: int = 0) -> List[Dict[str, Any]]:
        """Get discoveries by method"""
        return await self.find_many(
            query={"discovery_method": method},
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def update_discovery_result(self, website_url: str, policy_url: Optional[str] = None,
                                    discovery_method: Optional[str] = None,
                                    error: Optional[str] = None) -> int:
        """Update policy discovery result"""
        update_data = {}
        if policy_url is not None:
            update_data["policy_url"] = policy_url
        if discovery_method is not None:
            update_data["discovery_method"] = discovery_method
        if error is not None:
            update_data["error"] = error

        return await self.update_one({"website_url": website_url}, update_data)

    async def get_discovery_stats(self) -> Dict[str, Any]:
        """Get statistics about policy discoveries"""
        pipeline = [
            {
                "$group": {
                    "_id": "$discovery_method",
                    "count": {"$sum": 1}
                }
            }
        ]

        stats = await self.aggregate(pipeline)

        total_count = await self.count_documents()
        successful_count = await self.count_documents({"policy_url": {"$ne": None}, "error": None})
        failed_count = total_count - successful_count

        return {
            "total_discoveries": total_count,
            "successful_discoveries": successful_count,
            "failed_discoveries": failed_count,
            "by_method": {str(stat["_id"]): stat["count"] for stat in stats}
        }
