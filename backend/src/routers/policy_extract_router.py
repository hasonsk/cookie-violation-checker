from typing import Optional
from schemas.policy_schema import PolicyExtractResponse, PolicyExtractRequest
from fastapi import APIRouter, Depends
from controllers.policy_extract_controller import PolicyExtractController
from services.policy_extract_service.policy_extract_service import PolicyExtractService

router = APIRouter(prefix="/policy", tags=["policy"])

def get_policy_extract_service() -> PolicyExtractService:
    return PolicyExtractService()

def get_policy_extract_controller(
    policy_extract_service: PolicyExtractService = Depends(get_policy_extract_service)
) -> PolicyExtractController:
    return PolicyExtractController(policy_extract_service)

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
