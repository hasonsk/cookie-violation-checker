from typing import Dict, Any, List, Optional
from loguru import logger

from src.repositories.base import BaseRepository
from src.configs.settings import settings
from src.schemas.policy import PolicyContent

class PolicyContentRepository(BaseRepository):
    def __init__(self):
        super().__init__(settings.db.POLICY_CONTENTS_COLLECTION)

    async def create_policy_content(self, policy_content: Dict[str, Any]) -> str:
        """Create a new policy content record"""
        return await self.insert_one(policy_content)

    async def get_by_website_url(self, website_url: str) -> Optional[PolicyContent]:
        """Get policy content by website URL"""
        data = await self.find_one({"website_url": website_url})
        return PolicyContent(**data) if data else None

    async def get_latest_by_website_url(self, website_url: str) -> Optional[PolicyContent]:
        """Get latest policy content for a website"""
        results = await self.find_many(
            query={"website_url": website_url},
            limit=1,
            sort=[("created_at", -1)]
        )
        return PolicyContent(**results[0]) if results else None

    async def update_policy_content(self, website_url: str,
                                  original_content: Optional[str] = None,
                                  translated_content: Optional[str] = None,
                                  table_content: Optional[List[Dict[str, Any]]] = None,
                                  translated_table_content: Optional[str] = None) -> int:
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

        return await self.update_one({"website_url": website_url}, update_data)
