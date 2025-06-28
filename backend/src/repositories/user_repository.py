from typing import Dict, Any, List, Optional
from bson.objectid import ObjectId
from datetime import datetime

from src.repositories.base import BaseRepository
from src.configs.settings import settings

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(settings.db.USERS_COLLECTION)

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return await self.find_one({"email": email})

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information by user ID."""
        return await self.find_by_id(user_id)

    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user."""
        return await self.insert_one(user_data)

    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user information and return the updated user document."""
        return await self.find_one_and_update(
            {"_id": ObjectId(user_id)},
            update_data
        )


    async def get_all_users(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get all users, optionally filtered."""
        return await self.find_all(filters)
