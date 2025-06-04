import httpx
from loguru import logger
from exceptions.custom_exceptions import (
    PolicyDiscoveryError, PolicyExtractionError, FeatureExtractionError, ComplianceCheckError
)
from dotenv import load_dotenv
import os
from loguru import logger

load_dotenv()

API_BASE = os.getenv("API_BASE")

async def discover_policy(client: httpx.AsyncClient, website_url: str):
    logger.info(f"🔍 Discovering policy for {website_url}")
    resp = await client.post(f"{API_BASE}/policy/discover", json={"website_url": website_url})

    if resp.status_code != 200:
        logger.error(f"❌ Policy discovery failed: {resp.status_code}")
        raise PolicyDiscoveryError(status_code=resp.status_code)

    try:
        return resp.json()
    except Exception as e:
        raise Exception(f"Invalid JSON from policy discovery: {e}")

async def extract_policy(client: httpx.AsyncClient, website_url: str, policy_url: str):
    logger.info("📄 Extracting policy content")
    resp = await client.post(f"{API_BASE}/policy/extract", json={
        "website_url": website_url,
        "policy_url": policy_url,
    })

    if resp.status_code != 200:
        raise PolicyExtractionError(status_code=resp.status_code)

    try:
        return resp.json()
    except Exception as e:
        raise Exception(f"Invalid JSON from policy extract: {e}")

async def extract_features(client: httpx.AsyncClient, policy_content: dict):
    logger.info("🧠 Extracting cookie features")
    if policy_content.get("detected_language") != "en":
        json_data = {
            "policy_content": policy_content["translated_content"],
            "table_content": policy_content["translated_table_content"],
        }
    else:
        json_data = {
            "policy_content": policy_content["original_content"],
            "table_content": str(policy_content["table_content"]),
        }

    resp = await client.post(f"{API_BASE}/cookies/extract-features", json=json_data)
    if resp.status_code != 200:
        raise FeatureExtractionError(status_code=resp.status_code)

    try:
        return resp.json()
    except Exception as e:
        raise Exception(f"Invalid JSON from feature extract: {e}")

async def detect_violations(client: httpx.AsyncClient, website_url: str, features: dict, cookies: list):
    logger.info("🚨 Checking for cookie compliance violations")
    resp = await client.post(f"{API_BASE}/violations/detect", json={
        "website_url": website_url,
        "policy_json": features,
        "cookies": cookies
    })

    if resp.status_code != 200:
        raise ComplianceCheckError(status_code=resp.status_code)

    try:
        return resp.json()
    except Exception as e:
        raise Exception(f"Invalid JSON from violation detect: {e}")
