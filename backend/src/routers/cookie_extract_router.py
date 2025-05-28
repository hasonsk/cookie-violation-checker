from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from controllers.cookie_extract_controller import CookieExtractController

router = APIRouter(prefix="/cookies", tags=["cookies"])
controller = CookieExtractController()

class PolicyAnalysisRequest(BaseModel):
    policy_content: str
    table_content: Optional[str] = None

class DefaultFeaturesRequest(BaseModel):
    website_url: str

@router.post("/extract-features")
async def analyze_cookie_policy(request: PolicyAnalysisRequest):
    """Analyze cookie policy and extract features"""
    try:
        result = await controller.analyze_cookie_policy(
            request.policy_content,
            request.table_content
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
