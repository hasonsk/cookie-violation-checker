from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from . import BaseRepository
from ..connection import MongoDBConnection
from ..schemas import PolicyContentSchema

logger = logging.getLogger(__name__)

class PolicyContentRepository(BaseRepository):
    """Repository for policy content operations"""

    def __init__(self, db_connection: MongoDBConnection):
        super().__init__(db_connection, PolicyContentSchema.collection_name)

    async def create_policy_content(self, website_url: str, policy_url: Optional[str] = None,
                                  original_content: Optional[str] = None,
                                  translated_content: Optional[str] = None,
                                  table_content: Optional[List[Dict[str, Any]]] = None,
                                  translated_table_content: Optional[str] = None,
                                  error: Optional[str] = None) -> Dict[str, Any]:
        """Create a new policy content record"""
        document = PolicyContentSchema.create_document(
            website_url=website_url,
            policy_url=policy_url,
            original_content=original_content,
            translated_content=translated_content,
            table_content=table_content,
            translated_table_content=translated_table_content,
            error=error
        )
        return await self.create(document)

    async def get_by_website_url(self, website_url: str) -> Optional[Dict[str, Any]]:
        """Get policy content by website URL"""
        return await self.get_by_filter({"website_url": website_url})

    async def get_latest_by_website_url(self, website_url: str) -> Optional[Dict[str, Any]]:
        """Get latest policy content for a website"""
        results = await self.get_many(
            filter_dict={"website_url": website_url},
            limit=1,
            sort=[("created_at", -1)]
        )
        return results[0] if results else None

    async def get_by_policy_url(self, policy_url: str) -> Optional[Dict[str, Any]]:
        """Get policy content by policy URL"""
        return await self.get_by_filter({"policy_url": policy_url})

    async def get_policies_with_content(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get policies that have content extracted"""
        return await self.get_many(
            filter_dict={"$or": [
                {"original_content": {"$ne": None}},
                {"translated_content": {"$ne": None}},
                {"table_content": {"$ne": None}}
            ]},
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def get_policies_with_errors(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get policies that had extraction errors"""
        return await self.get_many(
            filter_dict={"error": {"$ne": None}},
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def get_policies_with_tables(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get policies that have table content"""
        return await self.get_many(
            filter_dict={"table_content": {"$ne": None, "$exists": True}},
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def update_policy_content(self, website_url: str,
                                  original_content: Optional[str] = None,
                                  translated_content: Optional[str] = None,
                                  table_content: Optional[List[Dict[str, Any]]] = None,
                                  translated_table_content: Optional[str] = None,
                                  error: Optional[str] = None) -> Optional[Dict[str, Any]]:
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

        return await self.update({"website_url": website_url}, update_data)

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

        return await self.crud.aggregate(pipeline)

    async def get_content_stats(self) -> Dict[str, Any]:
        """Get statistics about policy content"""
        total_count = await self.count()
        with_original = await self.count({"original_content": {"$ne": None}})
        with_translated = await self.count({"translated_content": {"$ne": None}})
        with_tables = await self.count({"table_content": {"$ne": None}})
        with_errors = await self.count({"error": {"$ne": None}})

        return {
            "total_policies": total_count,
            "with_original_content": with_original,
            "with_translated_content": with_translated,
            "with_table_content": with_tables,
            "with_errors": with_errors,
            "success_rate": (total_count - with_errors) / total_count * 100 if total_count > 0 else 0
        }
