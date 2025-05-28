from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

from controllers.policy_discovery_controller import PolicyDiscoveryController

router = APIRouter(prefix="/policy", tags=["policy"])
controller = PolicyDiscoveryController()

class PolicyRequest(BaseModel):
    website_url: str

class BulkPolicyRequest(BaseModel):
    website_urls: List[str]

@router.post("/discover")
async def find_policy(request: PolicyRequest):
    """Find cookie policy for a single website"""
    # print(f"🔍 Discovering policy for: {request.website_url}")
    try:
        result = await controller.find_single_policy(request.website_url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/discover-bulk")
async def find_policies_bulk(request: BulkPolicyRequest):
    """Find cookie policies for multiple websites"""
    try:
        results = await controller.find_multiple_policies(request.website_urls)
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
