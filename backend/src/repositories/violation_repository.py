import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from src.repositories.base import BaseRepository
from src.configs.settings import settings

class ViolationRepository(BaseRepository):
    """Repository for violation operations"""

    def __init__(self):
        super().__init__(settings.db.VIOLATIONS_COLLECTION)

    async def create_violation(self, document: Dict[str, Any]) -> str:
        """Create a new violation record"""
        return await self.insert_one(document)

    async def get_violations_by_website(self, website_url: str) -> List[Dict[str, Any]]:
        regex_pattern = f"^{re.escape(website_url)}"
        return await self.find_many(
            query={"website_url": {"$regex": regex_pattern}},
            sort=[("severity", 1), ("violation_type", 1), ("cookie_name", 1)]
        )
