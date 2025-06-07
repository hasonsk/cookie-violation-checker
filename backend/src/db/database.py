from motor.motor_asyncio import AsyncIOMotorClient
from configs.app_settings import get_mongodb_uri, validate_required_configs, DB_NAME

validate_required_configs()

# Create MongoDB client
client = AsyncIOMotorClient(get_mongodb_uri())
database = client[DB_NAME]

def get_database():
    return database

def get_collection(collection_name: str):
    return database[collection_name]
