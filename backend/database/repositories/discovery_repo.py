from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from . import BaseRepository
from ..connection import MongoDBConnection
from ..schemas import PolicyDiscoverySchema

logger = logging.getLogger(__name__)

class PolicyDiscoveryRepository(BaseRepository):
    """Repository for policy discovery operations"""

    def __init__(self, db_connection: MongoDBConnection):
        super().__init__(db_connection, PolicyDiscoverySchema.collection_name)

    async def create_discovery_result(self, website_url: str, policy_url: Optional[str] = None,
                                    discovery_method: str = "not_found",
                                    error: Optional[str] = None) -> Dict[str, Any]:
        """Create a new policy discovery result"""
        document = PolicyDiscoverySchema.create_document(
            website_url=website_url,
            policy_url=policy_url,
            discovery_method=discovery_method,
            error=error
        )
        return await self.create(document)

    async def get_by_website_url(self, website_url: str) -> Optional[Dict[str, Any]]:
        """Get policy discovery by website URL"""
        return await self.get_by_filter({"website_url": website_url})

    async def get_latest_by_website_url(self, website_url: str) -> Optional[Dict[str, Any]]:
        """Get latest policy discovery for a website"""
        results = await self.get_many(
            filter_dict={"website_url": website_url},
            limit=1,
            sort=[("created_at", -1)]
        )
        return results[0] if results else None

    async def get_successful_discoveries(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get all successful policy discoveries"""
        return await self.get_many(
            filter_dict={"policy_url": {"$ne": None}, "error": None},
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def get_failed_discoveries(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get all failed policy discoveries"""
        return await self.get_many(
            filter_dict={"$or": [{"policy_url": None}, {"error": {"$ne": None}}]},
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def get_by_discovery_method(self, method: str, limit: int = None) -> List[Dict[str, Any]]:
        """Get discoveries by method"""
        return await self.get_many(
            filter_dict={"discovery_method": method},
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def update_discovery_result(self, website_url: str, policy_url: Optional[str] = None,
                                    discovery_method: str = None,
                                    error: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Update policy discovery result"""
        update_data = {}
        if policy_url is not None:
            update_data["policy_url"] = policy_url
        if discovery_method is not None:
            update_data["discovery_method"] = discovery_method
        if error is not None:
            update_data["error"] = error

        return await self.update({"website_url": website_url}, update_data)

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

        stats = await self.crud.aggregate(pipeline)

        total_count = await self.count()
        successful_count = await self.count({"policy_url": {"$ne": None}, "error": None})
        failed_count = total_count - successful_count

        return {
            "total_discoveries": total_count,
            "successful_discoveries": successful_count,
            "failed_discoveries": failed_count,
            "by_method": {stat["_id"]: stat["count"] for stat in stats}
        }
