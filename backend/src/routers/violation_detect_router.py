from fastapi import APIRouter
from typing import List
from schemas.cookie_schema import ComplianceAnalysisResult, ComplianceRequest
from services.violation_detect_service.violation_detector import ViolationDetectorService

router = APIRouter(prefix="/violations", tags=["cookies"])
service = ViolationDetectorService()

@router.post("/detect", response_model=ComplianceAnalysisResult)
async def detect_violations(request: ComplianceRequest) -> ComplianceAnalysisResult:
    """
    Endpoint để nhận và phân tích cookies từ browser extension
    """
    print("hello")
    return await service.analyze_website_compliance(request.website_url, request.cookies, request.policy_json)
