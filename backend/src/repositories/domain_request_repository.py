from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId

from src.repositories.base import BaseRepository
from src.configs.settings import settings
from src.models.domain_request import DomainRequest # Import DomainRequest model

class DomainRequestRepository(BaseRepository):
    def __init__(self):
        super().__init__(settings.db.DOMAIN_REQUESTS_COLLECTION)

    async def get_all_domain_requests(self, filters: Optional[Dict] = None, skip: int = 0, limit: int = 100) -> List[DomainRequest]:
        query = filters if filters is not None else {}
        requests_data = await self.collection.find(query).skip(skip).limit(limit).to_list(length=limit)
        return [DomainRequest(**data) for data in requests_data]

    async def get_request_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.find_one({"user_id": ObjectId(user_id), "status": "pending"})

    async def get_domain_requests_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all domain requests for a given user ID.
        """
        return await self.find_all({"user_id": ObjectId(user_id)})

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

    async def create_domain_request(self, request_data: Dict[str, Any]) -> ObjectId:
        """
        Creates a new domain request entry in the database.
        """
        return await self.insert_one(request_data)

    async def get_domain_request_by_id(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a domain request by its ID.
        """
        return await self.find_by_id(request_id)
