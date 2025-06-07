from fastapi import APIRouter, Depends, HTTPException
from schemas.cookie_schema import CookieSubmissionRequest, ComplianceAnalysisResponse
from services.analyze_service.policy_cookies_analysis_service import PolicyCookiesAnalysisService, PolicyAnalysisError
from clients.internal_api_client import InternalAPIClient, APIConfig
from loguru import logger
from configs.app_settings import API_BASE
from fastapi import APIRouter, Depends, HTTPException
import time
import uuid

router = APIRouter(prefix="/analyze", tags=["analysis"])

def get_api_config() -> APIConfig:
    return APIConfig(api_base=API_BASE)

def get_internal_api_client(config: APIConfig = Depends(get_api_config)) -> InternalAPIClient:
    return InternalAPIClient(config=config)

def get_policy_analysis_service(api_client: InternalAPIClient = Depends(get_internal_api_client)) -> PolicyCookiesAnalysisService:
    return PolicyCookiesAnalysisService(api_client=api_client)

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
