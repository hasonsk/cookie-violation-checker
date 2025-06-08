from typing import Optional
from src.controllers.policy_extract_controller import PolicyExtractController
from src.schemas.policy_schema import PolicyExtractResponse, PolicyExtractRequest
from fastapi import APIRouter, Depends
from src.dependencies import get_policy_extract_controller

router = APIRouter(prefix="/policy", tags=["policy"])

@router.post("/extract", response_model=PolicyExtractResponse)
async def extract_policy_content(
    request: PolicyExtractRequest,
    policy_controller: PolicyExtractController = Depends(get_policy_extract_controller)
):
    """Extract policy content from website"""
    return await policy_controller.extract_policy(
        website_url=request.website_url,
        policy_url=request.policy_url,
        translate_to_english=request.translate_to_english,
        force_refresh=request.force_refresh
    )
