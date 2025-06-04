# repositories/user_repository.py
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Dict, Any, Optional

class UserRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin người dùng dựa trên email."""
        return await self.collection.find_one({"email": email})

    async def create_user(self, user_data: Dict[str, Any]) -> str:
        result = await self.collection.insert_one(user_data)
        return str(result.inserted_id)
