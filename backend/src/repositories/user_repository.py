from typing import Dict, Any, List, Optional
from bson.objectid import ObjectId
from datetime import datetime

from src.repositories.base_repository import BaseRepository
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

    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> int:
        """Update user information."""
        return await self.update_one(
            {"_id": ObjectId(user_id)},
            update_data
        )

    async def request_role_change(self, user_id: str, requested_role: str) -> int:
        """Request a role change for a user."""
        return await self.update_user(user_id, {"requested_role": requested_role})

    async def approve_account(self, user_id: str) -> int:
        """Approve a user account."""
        return await self.update_user(user_id, {"approved_by_admin": True})

    async def approve_role_change(self, user_id: str) -> int:
        """Approve a user's role change request."""
        user = await self.get_user_by_id(user_id)
        if user and user.get("requested_role"):
            modified_count = await self.update_user(user_id, {
                "role": user["requested_role"],
                "requested_role": None
            })
            return modified_count
        return 0

    async def get_all_users(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get all users, optionally filtered."""
        return await self.find_all(filters)
