from typing import Optional
from schemas.policy_schema import PolicyExtractResponse, PolicyExtractRequest
from fastapi import APIRouter
from controllers.policy_extract_controller import PolicyExtractController

router = APIRouter(prefix="/policy", tags=["policy"])
policy_controller = PolicyExtractController()


@router.post("/extract", response_model=PolicyExtractResponse)
async def extract_policy_content(request: PolicyExtractRequest):
    """Extract policy content from website"""
    return await policy_controller.extract_policy(
        website_url=request.website_url,
        policy_url=request.policy_url,
        translate_to_english=request.translate_to_english,
        force_refresh=request.force_refresh
    )
