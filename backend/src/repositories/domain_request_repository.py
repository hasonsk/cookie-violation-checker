from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId

from src.repositories.base import BaseRepository
from src.configs.settings import settings

class DomainRequestRepository(BaseRepository):
    def __init__(self):
        super().__init__(settings.db.DOMAIN_REQUESTS_COLLECTION) # Assuming this is the correct collection name

    async def get_all_requests(self) -> List[Dict[str, Any]]:
        return await self.find_all()

    async def get_request_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.find_one({"user_id": user_id, "status": "pending"})

    async def update_request_status(self, request_id: str, status: str, feedback: Optional[str] = None, processed_by: Optional[ObjectId] = None) -> int:
        update_fields = {"status": status, "processed_at": datetime.utcnow()}
        if feedback:
            update_fields["feedback"] = feedback
        if processed_by:
            update_fields["processed_by"] = processed_by

        return await self.update_one(
            {"_id": ObjectId(request_id)},
            update_fields
        )
