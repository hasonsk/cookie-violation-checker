from motor.motor_asyncio import AsyncIOMotorClient
from functools import lru_cache
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB_NAME]

@lru_cache()
def get_collection(name: str):
    return db[name]

def get_db():
    return client[MONGO_DB_NAME]
