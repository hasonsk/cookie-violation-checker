from datetime import datetime, timezone
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
        domain_requests = []
        for data in requests_data:
            # Ensure 'created_at' is present for older documents that might not have it
            if "created_at" not in data or data["created_at"] is None:
                data["created_at"] = datetime.now(timezone.utc)

            # Map 'user_id' from database to 'requester_id' for Pydantic model
            if "user_id" in data and "requester_id" not in data:
                data["requester_id"] = data.pop("user_id") # Use pop to remove user_id and assign to requester_id

            try:
                domain_requests.append(DomainRequest(**data))
            except Exception as e:
                # Log the error and the problematic data
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error validating DomainRequest data: {e}. Data: {data}")
                # Depending on desired behavior, you might re-raise, skip, or return partial results
                # For now, we'll re-raise to ensure the error is caught
                raise
        return domain_requests

    async def get_domain_requests_by_requester_id(self, requester_id: str, status: Optional[str] = None) -> List[DomainRequest]:
        """
        Retrieves domain requests for a given requester ID, optionally filtered by status.
        """
        filters = {"requester_id": ObjectId(requester_id)}
        if status:
            filters["status"] = status
        requests_data = await self.collection.find(filters).to_list(length=None) # Fetch all matching requests
        return [DomainRequest(**data) for data in requests_data]

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

    async def update_domain_request(self, request_id: str, update_data: Dict[str, Any]) -> int:
        """
        Updates an existing domain request in the database.
        """
        return await self.update_one(
            {"_id": ObjectId(request_id)},
            update_data
        )

    async def get_latest_domain_request_by_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the latest domain request for a given user.
        """
        return await self.collection.find_one(
            {"requester_id": ObjectId(user_id)},
            sort=[("created_at", -1)] # Sort by creation date descending to get the latest
        )

    async def get_domain_request_by_domain_and_status(self, domain: str, statuses: List[str], exclude_request_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Checks if a domain exists in any domain request with the given statuses.
        Optionally excludes a specific request ID.
        """
        query = {
            "domains": domain,
            "status": {"$in": statuses}
        }
        if exclude_request_id:
            query["_id"] = {"$ne": ObjectId(exclude_request_id)}
        return await self.collection.find_one(query)

    async def delete_domain_request(self, request_id: str) -> int:
        """
        Deletes a domain request by its ID.
        """
        return await self.delete_one({"_id": ObjectId(request_id)})
