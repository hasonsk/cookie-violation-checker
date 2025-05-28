from motor.motor_asyncio import AsyncIOMotorClient
from functools import lru_cache

MONGO_URI = "mongodb://admin:12345678@0.0.0.0:27017"
DB_NAME = "cookie_db"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

@lru_cache()
def get_collection(name: str):
    return db[name]
