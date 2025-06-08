from typing import Dict, Any, List, Optional
from loguru import logger

from src.repositories.base_repository import BaseRepository
from src.configs.settings import settings

class PolicyContentRepository(BaseRepository):
    def __init__(self):
        super().__init__(settings.db.POLICY_CONTENTS_COLLECTION)

    async def create_policy_content(self, policy_content: Dict[str, Any]) -> str:
        """Create a new policy content record"""
        return await self.insert_one(policy_content)

    async def get_by_website_url(self, website_url: str) -> Optional[Dict[str, Any]]:
        """Get policy content by website URL"""
        return await self.find_one({"website_url": website_url})

    async def get_latest_by_website_url(self, website_url: str) -> Optional[Dict[str, Any]]:
        """Get latest policy content for a website"""
        results = await self.find_many(
            query={"website_url": website_url},
            limit=1,
            sort=[("created_at", -1)]
        )
        return results[0] if results else None

    async def get_by_policy_url(self, policy_url: str) -> Optional[Dict[str, Any]]:
        """Get policy content by policy URL"""
        return await self.find_one({"policy_url": policy_url})

    async def get_policies_with_content(self, limit: int = 0) -> List[Dict[str, Any]]:
        """Get policies that have content extracted"""
        results = await self.find_many(
            query={"$or": [
                {"original_content": {"$ne": None}},
                {"translated_content": {"$ne": None}},
                {"table_content": {"$ne": None}}
            ]},
            limit=limit,
            sort=[("created_at", -1)]
        )
        return results

    async def get_policies_with_errors(self, limit: int = 0) -> List[Dict[str, Any]]:
        """Get policies that had extraction errors"""
        results = await self.find_many(
            query={"error": {"$ne": None}},
            limit=limit,
            sort=[("created_at", -1)]
        )
        return results

    async def get_policies_with_tables(self, limit: int = 0) -> List[Dict[str, Any]]:
        """Get policies that have table content"""
        results = await self.find_many(
            query={"table_content": {"$ne": None, "$exists": True}},
            limit=limit,
            sort=[("created_at", -1)]
        )
        return results

    async def update_policy_content(self, website_url: str,
                                  original_content: Optional[str] = None,
                                  translated_content: Optional[str] = None,
                                  table_content: Optional[List[Dict[str, Any]]] = None,
                                  translated_table_content: Optional[str] = None,
                                  error: Optional[str] = None) -> int:
        """Update policy content"""
        update_data = {}
        if original_content is not None:
            update_data["original_content"] = original_content
        if translated_content is not None:
            update_data["translated_content"] = translated_content
        if table_content is not None:
            update_data["table_content"] = table_content
        if translated_table_content is not None:
            update_data["translated_table_content"] = translated_table_content
        if error is not None:
            update_data["error"] = error

        return await self.update_one({"website_url": website_url}, update_data)

    async def search_content(self, search_term: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search in policy content"""
        pipeline = [
            {
                "$match": {
                    "$or": [
                        {"original_content": {"$regex": search_term, "$options": "i"}},
                        {"translated_content": {"$regex": search_term, "$options": "i"}}
                    ]
                }
            },
            {"$limit": limit},
            {"$sort": {"created_at": -1}}
        ]

        return await self.aggregate(pipeline)

    async def get_content_stats(self) -> Dict[str, Any]:
        """Get statistics about policy content"""
        total_count = await self.count_documents()
        with_original = await self.count_documents({"original_content": {"$ne": None}})
        with_translated = await self.count_documents({"translated_content": {"$ne": None}})
        with_tables = await self.count_documents({"table_content": {"$ne": None}})
        with_errors = await self.count_documents({"error": {"$ne": None}})

        return {
            "total_policies": total_count,
            "with_original_content": with_original,
            "with_translated_content": with_translated,
            "with_table_content": with_tables,
            "with_errors": with_errors,
            "success_rate": (total_count - with_errors) / total_count * 100 if total_count > 0 else 0
        }
