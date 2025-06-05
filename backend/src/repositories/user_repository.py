# repositories/user_repository.py
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Dict, Any, Optional
from schemas.auth_schema import User, UserRole
from bson.objectid import ObjectId
from datetime import datetime

class UserRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin người dùng dựa trên email."""
        return await self.collection.find_one({"email": email})

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information by user ID."""
        return await self.collection.find_one({"_id": ObjectId(user_id)})

    async def create_user(self, user_data: User) -> str:
        """Create a new user."""
        user_dict = user_data.model_dump(by_alias=True)
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()
        result = await self.collection.insert_one(user_dict)
        return str(result.inserted_id)

    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user information."""
        update_data["updated_at"] = datetime.utcnow()
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        return await self.get_user_by_id(user_id)

    async def request_role_change(self, user_id: str, requested_role: UserRole) -> Optional[Dict[str, Any]]:
        """Request a role change for a user."""
        return await self.update_user(user_id, {"requested_role": requested_role.value})

    async def approve_account(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Approve a user account."""
        return await self.update_user(user_id, {"approved_by_admin": True})

    async def approve_role_change(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Approve a user's role change request."""
        user = await self.get_user_by_id(user_id)
        if user and user.get("requested_role"):
            updated_user = await self.update_user(user_id, {
                "role": user["requested_role"],
                "requested_role": None
            })
            return updated_user
        return None
