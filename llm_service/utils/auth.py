import os
from dotenv import load_dotenv, find_dotenv
from fastapi import HTTPException, Request
from fastapi.security.api_key import APIKeyQuery

load_dotenv(find_dotenv())

VALID_API_KEYS = os.environ.get("LLM_API_KEYS", "secret-api-key")

api_key_query = APIKeyQuery(name="key", auto_error=False)

async def verify_api_key(request: Request, key: str = api_key_query):
    if key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return key
