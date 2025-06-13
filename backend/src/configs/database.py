from motor.motor_asyncio import AsyncIOMotorClient
from src.configs.settings import settings

# Create MongoDB client
client = AsyncIOMotorClient(settings.db.get_mongodb_uri())
database = client[settings.db.DB_NAME]

def get_database():
    return database

def get_collection(collection_name: str):
    return database[collection_name]
