# repositories/user_repository.py
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Dict, Any, Optional
from bson.objectid import ObjectId

class UserRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin người dùng dựa trên email."""
        return await self.collection.find_one({"email": email})

    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """Tạo người dùng mới và trả về ID."""
        result = await self.collection.insert_one(user_data)
        return str(result.inserted_id)

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin người dùng dựa trên ID."""
        return await self.collection.find_one({"_id": ObjectId(user_id)})
