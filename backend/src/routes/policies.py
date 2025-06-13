from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel

from src.schemas.policy import PolicyRequest, BulkPolicyRequest, PolicyExtractResponse, PolicyExtractRequest

from src.services.policy_crawler_service.policy_crawler_service import PolicyCrawlerService
from src.services.llm_services.policy_extractor_service import PolicyExtractorService
from src.dependencies.dependencies import get_policy_crawler_service, get_policy_extractor_service

router = APIRouter(prefix="/policy", tags=["policy"])

# @router.post("/discover")
# async def find_policy(
#     request: PolicyRequest,
#     policy_crawler_service: PolicyCrawlerService = Depends(get_policy_crawler_service)
# ):
#     """Find cookie policy for a single website"""
#     try:
#         result = await policy_crawler_service.find_single_policy(request.website_url)
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@router.post("/discover-bulk")
async def find_policies_bulk(
    request: BulkPolicyRequest,
    policy_crawler_service: PolicyCrawlerService = Depends(get_policy_crawler_service)
):
    """Find cookie policies for multiple websites"""
    try:
        results = await policy_crawler_service.find_multiple_policies(request.website_urls)
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract", response_model=PolicyExtractResponse)
async def extract_policy_content(
    request: PolicyExtractRequest,
    policy_extractor_service: PolicyExtractorService = Depends(get_policy_extractor_service)
):
    """Extract policy content from website"""
    return await policy_extractor_service.extract_policy(
        website_url=request.website_url,
        policy_url=request.policy_url,
        translate_to_english=request.translate_to_english,
        force_refresh=request.force_refresh
    )
