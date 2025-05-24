from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from bson import ObjectId
from pymongo import ReturnDocument
from motor.motor_asyncio import AsyncIOMotorCollection
import logging

from .connection import MongoDBConnection
from .schemas import MongoBaseSchema

logger = logging.getLogger(__name__)

class BaseCRUD:
    """Base CRUD operations for MongoDB collections"""

    def __init__(self, db_connection: MongoDBConnection, collection_name: str):
        self.db_connection = db_connection
        self.collection_name = collection_name
        self.collection: AsyncIOMotorCollection = db_connection.get_collection(collection_name)

    async def create(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document"""
        try:
            document['created_at'] = datetime.utcnow()
            document['updated_at'] = datetime.utcnow()

            result = await self.collection.insert_one(document)
            document['_id'] = result.inserted_id

            logger.info(f"Created document in {self.collection_name}: {result.inserted_id}")
            return document
        except Exception as e:
            logger.error(f"Error creating document in {self.collection_name}: {str(e)}")
            raise

    async def create_many(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple documents"""
        try:
            current_time = datetime.utcnow()
            for doc in documents:
                doc['created_at'] = current_time
                doc['updated_at'] = current_time

            result = await self.collection.insert_many(documents)

            for i, doc in enumerate(documents):
                doc['_id'] = result.inserted_ids[i]

            logger.info(f"Created {len(documents)} documents in {self.collection_name}")
            return documents
        except Exception as e:
            logger.error(f"Error creating documents in {self.collection_name}: {str(e)}")
            raise

    async def find_one(self, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document"""
        try:
            document = await self.collection.find_one(filter_dict)
            if document:
                document['_id'] = str(document['_id'])
            return document
        except Exception as e:
            logger.error(f"Error finding document in {self.collection_name}: {str(e)}")
            raise

    async def find_many(self, filter_dict: Dict[str, Any] = None,
                       limit: int = None, skip: int = None,
                       sort: List[tuple] = None) -> List[Dict[str, Any]]:
        """Find multiple documents"""
        try:
            cursor = self.collection.find(filter_dict or {})

            if sort:
                cursor = cursor.sort(sort)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)

            documents = await cursor.to_list(length=limit)

            for doc in documents:
                doc['_id'] = str(doc['_id'])

            return documents
        except Exception as e:
            logger.error(f"Error finding documents in {self.collection_name}: {str(e)}")
            raise

    async def update_one(self, filter_dict: Dict[str, Any],
                        update_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a single document"""
        try:
            update_dict['updated_at'] = datetime.utcnow()

            result = await self.collection.find_one_and_update(
                filter_dict,
                {"$set": update_dict},
                return_document=ReturnDocument.AFTER
            )

            if result:
                result['_id'] = str(result['_id'])
                logger.info(f"Updated document in {self.collection_name}")

            return result
        except Exception as e:
            logger.error(f"Error updating document in {self.collection_name}: {str(e)}")
            raise

    async def update_many(self, filter_dict: Dict[str, Any],
                         update_dict: Dict[str, Any]) -> int:
        """Update multiple documents"""
        try:
            update_dict['updated_at'] = datetime.utcnow()

            result = await self.collection.update_many(
                filter_dict,
                {"$set": update_dict}
            )

            logger.info(f"Updated {result.modified_count} documents in {self.collection_name}")
            return result.modified_count
        except Exception as e:
            logger.error(f"Error updating documents in {self.collection_name}: {str(e)}")
            raise

    async def delete_one(self, filter_dict: Dict[str, Any]) -> bool:
        """Delete a single document"""
        try:
            result = await self.collection.delete_one(filter_dict)
            success = result.deleted_count > 0

            if success:
                logger.info(f"Deleted document from {self.collection_name}")

            return success
        except Exception as e:
            logger.error(f"Error deleting document from {self.collection_name}: {str(e)}")
            raise

    async def delete_many(self, filter_dict: Dict[str, Any]) -> int:
        """Delete multiple documents"""
        try:
            result = await self.collection.delete_many(filter_dict)

            logger.info(f"Deleted {result.deleted_count} documents from {self.collection_name}")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting documents from {self.collection_name}: {str(e)}")
            raise

    async def count(self, filter_dict: Dict[str, Any] = None) -> int:
        """Count documents"""
        try:
            count = await self.collection.count_documents(filter_dict or {})
            return count
        except Exception as e:
            logger.error(f"Error counting documents in {self.collection_name}: {str(e)}")
            raise

    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform aggregation"""
        try:
            cursor = self.collection.aggregate(pipeline)
            documents = await cursor.to_list(length=None)

            for doc in documents:
                if '_id' in doc and isinstance(doc['_id'], ObjectId):
                    doc['_id'] = str(doc['_id'])

            return documents
        except Exception as e:
            logger.error(f"Error in aggregation for {self.collection_name}: {str(e)}")
            raise

    async def find_by_id(self, object_id: str) -> Optional[Dict[str, Any]]:
        """Find document by ObjectId"""
        try:
            document = await self.collection.find_one({"_id": ObjectId(object_id)})
            if document:
                document['_id'] = str(document['_id'])
            return document
        except Exception as e:
            logger.error(f"Error finding document by id in {self.collection_name}: {str(e)}")
            raise

    async def exists(self, filter_dict: Dict[str, Any]) -> bool:
        """Check if document exists"""
        try:
            count = await self.collection.count_documents(filter_dict, limit=1)
            return count > 0
        except Exception as e:
            logger.error(f"Error checking existence in {self.collection_name}: {str(e)}")
            raise

    async def distinct(self, field: str, filter_dict: Dict[str, Any] = None) -> List[Any]:
        """Get distinct values for a field"""
        try:
            values = await self.collection.distinct(field, filter_dict or {})
            return values
        except Exception as e:
            logger.error(f"Error getting distinct values in {self.collection_name}: {str(e)}")
            raise

    async def bulk_write(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform bulk write operations"""
        try:
            from pymongo import UpdateOne, InsertOne, DeleteOne, ReplaceOne

            bulk_ops = []
            for op in operations:
                if op['operation'] == 'insert':
                    op['document']['created_at'] = datetime.utcnow()
                    op['document']['updated_at'] = datetime.utcnow()
                    bulk_ops.append(InsertOne(op['document']))
                elif op['operation'] == 'update':
                    op['update']['updated_at'] = datetime.utcnow()
                    bulk_ops.append(UpdateOne(op['filter'], {"$set": op['update']}))
                elif op['operation'] == 'replace':
                    op['document']['updated_at'] = datetime.utcnow()
                    bulk_ops.append(ReplaceOne(op['filter'], op['document']))
                elif op['operation'] == 'delete':
                    bulk_ops.append(DeleteOne(op['filter']))

            result = await self.collection.bulk_write(bulk_ops)

            return {
                "inserted_count": result.inserted_count,
                "modified_count": result.modified_count,
                "deleted_count": result.deleted_count,
                "upserted_count": result.upserted_count
            }
        except Exception as e:
            logger.error(f"Error in bulk write for {self.collection_name}: {str(e)}")
            raise


class CRUDFactory:
    """Factory class to create CRUD instances"""

    def __init__(self, db_connection: MongoDBConnection):
        self.db_connection = db_connection
        self._crud_instances = {}

    def get_crud(self, collection_name: str) -> BaseCRUD:
        """Get or create CRUD instance for collection"""
        if collection_name not in self._crud_instances:
            self._crud_instances[collection_name] = BaseCRUD(
                self.db_connection, collection_name
            )
        return self._crud_instances[collection_name]
