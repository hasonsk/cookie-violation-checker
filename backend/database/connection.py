from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger
from typing import Optional, Dict, Any
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from contextlib import asynccontextmanager
import os
from functools import lru_cache
from datetime import datetime

class MongoDBConnection:
    """
    MongoDB connection manager for the Cookie Violations Check system.
    Uses Motor for async MongoDB operations.
    """
    def __init__(self, connection_string: str = None, db_name: str = None):
        """Initialize MongoDB connection with provided credentials or environment variables"""
        self.connection_string = connection_string or os.getenv("MONGODB_CONNECTION_STRING")
        if not self.connection_string:
            raise ValueError("MongoDB connection string not provided")

        self.db_name = db_name or os.getenv("MONGODB_DATABASE", "cookie_violations")
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self._connection_ready = False

    async def connect(self) -> None:
        """Establish connection to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=45000,
                maxPoolSize=100,
                minPoolSize=10,
                retryWrites=True
            )

            # Verify connection by fetching server info
            await self.client.server_info()
            self.db = self.client[self.db_name]
            self._connection_ready = True

            # Create indexes after connection
            await self.create_indexes()

            logger.info(f"Connected to MongoDB database: {self.db_name}")

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self._connection_ready = False
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    async def close(self) -> None:
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self._connection_ready = False
            logger.info("MongoDB connection closed")

    @property
    def is_connected(self) -> bool:
        """Check if MongoDB connection is established"""
        return self._connection_ready and self.client is not None

    def get_collection(self, collection_name: str):
        """Get collection from database"""
        if not self._connection_ready:
            raise ConnectionError("MongoDB connection not established")
        return self.db[collection_name]

    async def create_indexes(self):
        """Create necessary indexes for performance"""
        if not self._connection_ready:
            raise ConnectionError("MongoDB connection not established")

        try:
            # Task collection indexes
            await self.db.tasks.create_index("task_id", unique=True)
            await self.db.tasks.create_index("status")
            await self.db.tasks.create_index("created_at")

            # Policy discovery collection indexes
            await self.db.policy_discoveries.create_index("website_url")
            await self.db.policy_discoveries.create_index("policy_url")
            await self.db.policy_discoveries.create_index("discovery_method")
            await self.db.policy_discoveries.create_index("created_at")

            # Policy content collection indexes
            await self.db.policy_contents.create_index("website_url")
            await self.db.policy_contents.create_index("policy_url")
            await self.db.policy_contents.create_index("created_at")

            # Cookie features collection indexes
            await self.db.cookie_features.create_index("website_url")
            await self.db.cookie_features.create_index("name")
            await self.db.cookie_features.create_index("feature_type")
            await self.db.cookie_features.create_index("created_at")

            # Live cookies collection indexes
            await self.db.live_cookies.create_index("website_url")
            await self.db.live_cookies.create_index("name")
            await self.db.live_cookies.create_index("domain")
            await self.db.live_cookies.create_index("collected_at")
            await self.db.live_cookies.create_index([("name", 1), ("domain", 1)])

            # Violations collection indexes
            await self.db.violations.create_index("website_url")
            await self.db.violations.create_index("cookie_name")
            await self.db.violations.create_index("violation_type")
            await self.db.violations.create_index("feature_type")
            await self.db.violations.create_index("severity")
            await self.db.violations.create_index("created_at")
            await self.db.violations.create_index([("cookie_name", 1), ("website_url", 1)])

            # Website reports collection indexes
            await self.db.website_reports.create_index("website_url")
            await self.db.website_reports.create_index("scan_time")
            await self.db.website_reports.create_index("policy_found")
            await self.db.website_reports.create_index("total_cookies")
            await self.db.website_reports.create_index("violating_cookies")

            logger.info("MongoDB indexes created successfully")

        except Exception as e:
            logger.error(f"Failed to create indexes: {str(e)}")
            raise

    async def ping(self) -> Dict[str, Any]:
        """Ping database to check connection status"""
        if not self._connection_ready:
            return {"status": "disconnected"}

        try:
            result = await self.client.admin.command('ping')
            return {
                "status": "connected",
                "ping": result,
                "database": self.db_name,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to ping MongoDB: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        if not self._connection_ready:
            return {"status": "disconnected"}

        try:
            stats = await self.db.command("dbStats")
            collections = await self.db.list_collection_names()

            return {
                "database": self.db_name,
                "collections": len(collections),
                "collection_names": collections,
                "data_size": stats.get("dataSize", 0),
                "storage_size": stats.get("storageSize", 0),
                "indexes": stats.get("indexes", 0),
                "objects": stats.get("objects", 0)
            }
        except Exception as e:
            logger.error(f"Failed to get database stats: {str(e)}")
            return {"status": "error", "message": str(e)}


# Global connection instance
_db_connection: Optional[MongoDBConnection] = None

async def get_database() -> MongoDBConnection:
    """Get database connection instance"""
    global _db_connection

    if _db_connection is None:
        _db_connection = MongoDBConnection()
        await _db_connection.connect()

    if not _db_connection.is_connected:
        await _db_connection.connect()

    return _db_connection

async def close_database():
    """Close database connection"""
    global _db_connection
    if _db_connection:
        await _db_connection.close()
        _db_connection = None

@asynccontextmanager
async def get_db():
    """Context manager for database operations"""
    db_conn = await get_database()
    try:
        yield db_conn
    except Exception as e:
        logger.error(f"Database operation error: {str(e)}")
        raise
    # Connection is managed globally, don't close here
