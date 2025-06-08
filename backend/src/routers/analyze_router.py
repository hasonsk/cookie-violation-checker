from fastapi import APIRouter, Depends, HTTPException
from src.schemas.cookie_schema import CookieSubmissionRequest, ComplianceAnalysisResponse
from src.services.analyze_service.policy_cookies_analysis_service import PolicyCookiesAnalysisService
from src.exceptions.custom_exceptions import PolicyAnalysisError
from loguru import logger
from fastapi import APIRouter, Depends, HTTPException
import time
import uuid
from src.dependencies import (
    get_policy_discovery_service,
    get_policy_extract_service,
    get_cookie_extractor_service,
    get_violation_detector_service,
    get_violation_repository # Add this import
)
from src.services.policy_discover_service.policy_discovery_service import PolicyDiscoveryService
from src.services.policy_extract_service.policy_extract_service import PolicyExtractService
from src.services.cookies_extract_service.cookies_extractor import CookieExtractorService
from src.services.violation_detect_service.violation_detector_service import ViolationDetectorService
from src.repositories.violation_repo import ViolationRepository

router = APIRouter(prefix="/analyze", tags=["analysis"])

def get_policy_analysis_service(
    discovery_service: PolicyDiscoveryService = Depends(get_policy_discovery_service),
    extract_service: PolicyExtractService = Depends(get_policy_extract_service),
    feature_service: CookieExtractorService = Depends(get_cookie_extractor_service),
    violation_service: ViolationDetectorService = Depends(get_violation_detector_service),
    violation_repo: ViolationRepository = Depends(get_violation_repository) # Add this dependency
) -> PolicyCookiesAnalysisService:
    return PolicyCookiesAnalysisService(
        discovery_service=discovery_service,
        extract_service=extract_service,
        feature_service=feature_service,
        violation_service=violation_service,
        violation_repo=violation_repo # Pass the repository
    )

@router.post("/", response_model=ComplianceAnalysisResponse)
async def analyze_policy(
    payload: CookieSubmissionRequest,
    service: PolicyCookiesAnalysisService = Depends(get_policy_analysis_service)
) -> ComplianceAnalysisResponse:
    """
    Endpoint to receive and analyze cookies from a browser extension,
    orchestrating the entire policy compliance analysis process.
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())
    logger.info(
      "Analysis request received",
      extra={
        "request_id": request_id,
        "website_url": payload.website_url,
        "cookies_count": len(payload.cookies)
      }
    )

    try:
      analysis_result = await service.orchestrate_analysis(payload, request_id)
      return analysis_result
    except PolicyAnalysisError as e:
      logger.error(
        "Analysis failed in router",
        extra={
          "request_id": request_id,
          "phase": e.phase.value,
          "error": e.message,
          "status_code": e.status_code,
          "execution_time": time.time() - start_time
        }
      )
      raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
      logger.error(e)
      logger.error(
        "Unexpected error in router during analysis",
        extra={
          "request_id": request_id,
          "error": str(e),
          "execution_time": time.time() - start_time
        }
      )
      raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
