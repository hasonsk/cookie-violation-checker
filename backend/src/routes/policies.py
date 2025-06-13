from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel

from src.schemas.policy import PolicyRequest, BulkPolicyRequest, PolicyExtractResponse, PolicyExtractRequest

from src.services.policy_crawler_service.policy_crawler_service import PolicyCrawlerService
from src.services.policy_crawler_service.crawler_factory import CrawlerFactory
from src.services.llm_services.policy_llm_service import PolicyLLMService
from src.dependencies.dependencies import create_playwright_bing_extractor, get_policy_content_repository
from src.repositories.policy_content_repository import PolicyContentRepository

router = APIRouter(prefix="/policy", tags=["policy"])

@router.post("/discovery", response_model=PolicyExtractResponse)
async def analyze_website_policy(
    website_url: str,
    force_refresh: bool = False,
    policy_content_repo: PolicyContentRepository = Depends(get_policy_content_repository),
    extractor: PolicyCrawlerService = Depends(create_playwright_bing_extractor)
):
    """Analyze and extract cookie policy for a given website URL."""
    try:
        result = await extractor.extract_policy(website_url, force_refresh)
        if result:
            return PolicyExtractResponse(
                website_url=result.website_url,
                policy_url=result.policy_url,
                original_content=result.original_content,
                translated_content=result.translated_content,
                detected_language=result.detected_language,
                table_content=result.table_content,
                translated_table_content=result.translated_table_content,
                error=result.error
            )
        else:
            raise HTTPException(status_code=404, detail="Policy not found or extraction failed.")
    except Exception as e:
        # Assuming logger is defined elsewhere or needs to be imported
        # For now, I'll just raise the HTTPException
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# The /discover-bulk and /extract endpoints need to be re-evaluated
# based on the new PolicyExtractor's capabilities.
# For now, I'm commenting them out to avoid immediate errors.
# @router.post("/discover-bulk")
# async def find_policies_bulk(
#     request: BulkPolicyRequest,
#     policy_crawler: PolicyCrawlerService = Depends(get_policy_crawler)
# ):
#     """Find cookie policies for multiple websites"""
#     try:
#         # This logic needs to be adapted to use the new PolicyExtractor
#         # It might involve iterating through website_urls and calling policy_extractor.extract_policy for each.
#         results = []
#         for url in request.website_urls:
#             policy_content = await policy_crawler.extract_policy(url)
#             if policy_content:
#                 results.append(policy_content.dict())
#         return {"success": True, "data": results}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post("/extract", response_model=PolicyExtractResponse)
# async def extract_policy_content(
#     request: PolicyExtractRequest,
#     policy_extractor_service: PolicyLLMService = Depends(get_policy_extractor_service)
# ):
#     """Extract policy content from website"""
#     # This endpoint might be redundant or need significant re-work
#     # if the new /analyze-website endpoint covers its functionality.
#     return await policy_extractor_service.extract_policy(
#         website_url=request.website_url,
#         policy_url=request.policy_url,
#         translate_to_english=request.translate_to_english,
#         force_refresh=request.force_refresh
#     )
