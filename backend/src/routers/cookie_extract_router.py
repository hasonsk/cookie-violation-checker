from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from src.schemas.policy_schema import PolicyAnalysisRequest

from src.controllers.cookie_extract_controller import CookieExtractController
from src.services.cookies_extract_service.cookies_extractor import CookieExtractorService

router = APIRouter(prefix="/cookies", tags=["cookies"])

def get_cookie_extractor_service() -> CookieExtractorService:
    return CookieExtractorService()

def get_cookie_extract_controller(
    extractor_service: CookieExtractorService = Depends(get_cookie_extractor_service)
) -> CookieExtractController:
    return CookieExtractController(extractor_service)

@router.post("/extract-features")
async def analyze_cookie_policy(
    request: PolicyAnalysisRequest,
    controller: CookieExtractController = Depends(get_cookie_extract_controller)
):
    """Analyze cookie policy and extract features"""
    try:
        result = await controller.analyze_cookie_policy(
            request.policy_content,
            request.table_content
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
