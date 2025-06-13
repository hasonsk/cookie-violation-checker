from fastapi import APIRouter, Depends, HTTPException
from src.schemas.cookie import CookieSubmissionRequest
from src.schemas.violation import ComplianceAnalysisResponse
from src.services.violation_analyzer_service.violation_analyzer_service import ViolationAnalyzerService
from src.exceptions.custom_exceptions import PolicyAnalysisError
from loguru import logger
import time
import uuid
from src.dependencies.dependencies import get_violation_analyzer_service

router = APIRouter(prefix="/violations", tags=["Violations"])

@router.post("/analyze", response_model=ComplianceAnalysisResponse)
async def analyze_policy(
    payload: CookieSubmissionRequest,
    service: ViolationAnalyzerService = Depends(get_violation_analyzer_service)
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
      logger.error(str(e))
      logger.error(
        "Unexpected error in router during analysis",
        extra={
          "request_id": request_id,
          "error": str(e),
          "execution_time": time.time() - start_time
        }
      )
      raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
