from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from ..connection import MongoDBConnection
from ..crud import BaseCRUD

class BaseRepository:
    """Base repository class with common operations"""

    def __init__(self, db_connection: MongoDBConnection, collection_name: str):
        self.db_connection = db_connection
        self.collection_name = collection_name
        self.crud = BaseCRUD(db_connection, collection_name)

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record"""
        return await self.crud.create(data)

    async def get_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get record by ID"""
        return await self.crud.find_by_id(record_id)

    async def get_by_filter(self, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get single record by filter"""
        return await self.crud.find_one(filter_dict)

    async def get_many(self, filter_dict: Dict[str, Any] = None,
                      limit: int = None, skip: int = None,
                      sort: List[tuple] = None) -> List[Dict[str, Any]]:
        """Get multiple records"""
        return await self.crud.find_many(filter_dict, limit, skip, sort)

    async def update(self, filter_dict: Dict[str, Any],
                    update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a record"""
        return await self.crud.update_one(filter_dict, update_data)

    async def delete(self, filter_dict: Dict[str, Any]) -> bool:
        """Delete a record"""
        return await self.crud.delete_one(filter_dict)

    async def count(self, filter_dict: Dict[str, Any] = None) -> int:
        """Count records"""
        return await self.crud.count(filter_dict)

    async def exists(self, filter_dict: Dict[str, Any]) -> bool:
        """Check if record exists"""
        return await self.crud.exists(filter_dict)
