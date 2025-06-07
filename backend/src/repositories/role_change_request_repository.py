from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId

from repositories.base_repository import BaseRepository
from configs.app_settings import ROLE_CHANGE_REQUESTS_COLLECTION

class RoleChangeRequestRepository(BaseRepository):
    def __init__(self):
        super().__init__(ROLE_CHANGE_REQUESTS_COLLECTION)

    async def create_role_change_request(self, request_data: Dict[str, Any]) -> str:
        return await self.insert_one(request_data)

    async def get_request_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.find_one({"user_id": user_id, "status": "pending"})

    async def update_request_status(self, request_id: str, status: str, admin_notes: Optional[str] = None, reviewed_by: Optional[str] = None) -> int:
        update_fields = {"status": status, "reviewed_at": datetime.utcnow()}
        if admin_notes:
            update_fields["admin_notes"] = admin_notes
        if reviewed_by:
            update_fields["reviewed_by"] = reviewed_by

        return await self.update_one(
            {"_id": ObjectId(request_id)},
            update_fields
        )
