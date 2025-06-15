from typing import Dict, Optional, List
from bson import ObjectId
from src.repositories.base import BaseRepository
from src.models.website import Website
from src.configs.settings import settings

class WebsiteRepository(BaseRepository):
    def __init__(self):
        super().__init__(settings.db.WEBSITES_COLLECTION)

    async def get_website_by_root_url(self, root_url: str) -> Optional[Website]:
        """
        Retrieves a website by its root URL (domain).
        """
        website_data = await self.collection.find_one({"domain": root_url})
        if website_data:
            return Website(**website_data)
        return None

    async def update_website_fields(self, website_id: str, update_data: Dict) -> Optional[Website]:
        """
        Updates specific fields of an existing website entry.
        """
        result = await self.collection.update_one(
            {"_id": ObjectId(website_id)},
            {"$set": update_data}
        )
        if result.modified_count:
            updated_website_data = await self.collection.find_one({"_id": ObjectId(website_id)})
            return Website(**updated_website_data)
        return None

    async def create_website(self, website_data: Dict) -> Website:
        """
        Creates a new website entry in the database.
        """
        result = await self.collection.insert_one(website_data)
        website_data["_id"] = result.inserted_id
        return Website(**website_data)

    async def update_website(self, website_id: str, update_data: Dict) -> Optional[Website]:
        """
        Updates an existing website entry.
        """
        # Ensure ObjectId is used for _id
        if "_id" in update_data:
            del update_data["_id"]

        result = await self.collection.update_one(
            {"_id": ObjectId(website_id)},
            {"$set": update_data}
        )
        if result.modified_count:
            updated_website_data = await self.collection.find_one({"_id": ObjectId(website_id)})
            return Website(**updated_website_data)
        return None

    async def get_all_websites(self, filters: Optional[Dict] = None, skip: int = 0, limit: int = 100) -> List[Website]:
        """
        Retrieves a list of all websites, with optional filtering, skipping, and limiting.
        """
        query = filters if filters is not None else {}
        websites_data = await self.collection.find(query).skip(skip).limit(limit).to_list(length=limit)
        return [Website(**data) for data in websites_data]

    async def get_website_by_id(self, website_id: str) -> Optional[Website]:
        """
        Retrieves a website by its ID.
        """
        website_data = await self.collection.find_one({"_id": ObjectId(website_id)})
        if website_data:
            return Website(**website_data)
        return None
