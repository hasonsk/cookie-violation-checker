from configs.database import get_collection
from schemas.policy_schema import PolicyContent

async def save_policy_content(content: PolicyContent) -> str:
    collection = get_collection("policies")
    result = await collection.insert_one(content.dict())
    return str(result.inserted_id)

async def get_policy_by_url(website_url: str):
    collection = get_collection("policies")
    return await collection.find_one({"website_url": website_url})
