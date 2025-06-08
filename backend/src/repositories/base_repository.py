from typing import Any, Dict, List, Optional
from bson import ObjectId
from src.db.database import get_collection

class BaseRepository:
    def __init__(self, collection_name: str):
        self.collection = get_collection(collection_name)

    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one(query)

    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"_id": ObjectId(id)})

    async def find_all(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if query is None:
            query = {}
        return await self.collection.find(query).to_list(length=None)

    async def find_many(self, query: Optional[Dict[str, Any]] = None, limit: int = 0, sort: Optional[List[tuple]] = None) -> List[Dict[str, Any]]:
        if query is None:
            query = {}
        cursor = self.collection.find(query)
        if sort:
            cursor = cursor.sort(sort)
        if limit > 0:
            cursor = cursor.limit(limit)
        return await cursor.to_list(length=None)

    async def insert_one(self, document: Dict[str, Any]) -> str:
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def insert_many(self, documents: List[Dict[str, Any]]) -> List[str]:
        result = await self.collection.insert_many(documents)
        return [str(id) for id in result.inserted_ids]

    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return await self.collection.aggregate(pipeline).to_list(length=None)

    async def count_documents(self, query: Optional[Dict[str, Any]] = None) -> int:
        if query is None:
            query = {}
        return await self.collection.count_documents(query)

    async def update_one(self, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        result = await self.collection.update_one(query, {"$set": update})
        return result.modified_count

    async def delete_one(self, query: Dict[str, Any]) -> int:
        result = await self.collection.delete_one(query)
        return result.deleted_count

    async def delete_many(self, query: Dict[str, Any]) -> int:
        result = await self.collection.delete_many(query)
        return result.deleted_count
