from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel

from src.schemas.policy import PolicyExtractResponse, PolicyExtractRequest

from src.services.policy_crawler_service.policy_crawler_service import PolicyCrawlerService
from src.services.policy_crawler_service.crawler_factory import CrawlerFactory
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
