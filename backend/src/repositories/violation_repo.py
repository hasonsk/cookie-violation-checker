from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from src.repositories.base_repository import BaseRepository
from src.configs.settings import settings

class ViolationRepository(BaseRepository):
    """Repository for violation operations"""

    def __init__(self):
        super().__init__(settings.db.VIOLATIONS_COLLECTION) # Assuming "violations" is the collection name

    async def create_violation(self, document: Dict[str, Any]) -> str:
        """Create a new violation record"""
        return await self.insert_one(document)

    async def create_many_violations(self, violations: List[Dict[str, Any]]) -> List[str]:
        """Create multiple violations"""
        return await self.insert_many(violations)

    async def get_violations_by_website(self, website_url: str) -> List[Dict[str, Any]]:
        """Get all violations for a website"""
        return await self.find_many(
            query={"website_url": website_url},
            sort=[("severity", 1), ("violation_type", 1), ("cookie_name", 1)]
        )

    async def get_violations_by_cookie(self, website_url: str, cookie_name: str) -> List[Dict[str, Any]]:
        """Get violations for a specific cookie"""
        return await self.find_many(
            query={"website_url": website_url, "cookie_name": cookie_name},
            sort=[("severity", 1), ("violation_type", 1)]
        )

    async def get_violations_by_type(self, violation_type: str, limit: int = 0) -> List[Dict[str, Any]]:
        """Get violations by type"""
        return await self.find_many(
            query={"violation_type": violation_type},
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def get_violations_by_severity(self, severity: str, limit: int = 0) -> List[Dict[str, Any]]:
        """Get violations by severity"""
        return await self.find_many(
            query={"severity": severity},
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def get_high_severity_violations(self, limit: int = 0) -> List[Dict[str, Any]]:
        """Get high severity violations"""
        return await self.get_violations_by_severity("high", limit)

    async def get_recent_violations(self, hours_ago: int = 24, limit: int = 0) -> List[Dict[str, Any]]:
        """Get recent violations within specified hours"""
        time_threshold = datetime.utcnow() - timedelta(hours=hours_ago)
        return await self.find_many(
            query={"created_at": {"$gte": time_threshold}},
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def get_violation_summary_by_website(self, website_url: str) -> Dict[str, Any]:
        """Get violation summary for a website"""
        pipeline = [
            {"$match": {"website_url": website_url}},
            {
                "$group": {
                    "_id": {
                        "violation_type": "$violation_type",
                        "severity": "$severity"
                    },
                    "count": {"$sum": 1}
                }
            }
        ]

        results = await self.aggregate(pipeline)

        summary = {
            "total_violations": len(results),
            "by_type": {},
            "by_severity": {},
            "by_feature_type": {}
        }

        for result in results:
            v_type = result["_id"]["violation_type"]
            severity = result["_id"]["severity"]
            count = result["count"]

            summary["by_type"][v_type] = summary["by_type"].get(v_type, 0) + count
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + count

        # Get feature type breakdown
        feature_pipeline = [
            {"$match": {"website_url": website_url}},
            {"$group": {"_id": "$feature_type", "count": {"$sum": 1}}}
        ]

        feature_results = await self.aggregate(feature_pipeline)
        for result in feature_results:
            summary["by_feature_type"][result["_id"]] = result["count"]

        return summary

    async def delete_violations_by_website(self, website_url: str) -> int:
        """Delete all violations for a website"""
        return await self.delete_many({"website_url": website_url})
