from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from src.schemas.policy_schema import PolicyRequest, BulkPolicyRequest

from src.controllers.policy_discovery_controller import PolicyDiscoveryController
from src.services.policy_discover_service.policy_discovery_service import PolicyDiscoveryService
from src.dependencies import get_policy_discovery_repository

router = APIRouter(prefix="/policy", tags=["policy"])

async def get_policy_discovery_service() -> PolicyDiscoveryService:
    discovery_repo = get_policy_discovery_repository()
    async with PolicyDiscoveryService(discovery_repo=discovery_repo) as service:
        yield service

async def get_policy_discovery_controller(
    policy_service: PolicyDiscoveryService = Depends(get_policy_discovery_service)
) -> PolicyDiscoveryController:
    return PolicyDiscoveryController(policy_service)

@router.post("/discover")
async def find_policy(
    request: PolicyRequest,
    controller: PolicyDiscoveryController = Depends(get_policy_discovery_controller)
):
    """Find cookie policy for a single website"""
    # print(f"🔍 Discovering policy for: {request.website_url}")
    try:
        result = await controller.find_single_policy(request.website_url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/discover-bulk")
async def find_policies_bulk(
    request: BulkPolicyRequest,
    controller: PolicyDiscoveryController = Depends(get_policy_discovery_controller)
):
    """Find cookie policies for multiple websites"""
    try:
        results = await controller.find_multiple_policies(request.website_urls)
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
