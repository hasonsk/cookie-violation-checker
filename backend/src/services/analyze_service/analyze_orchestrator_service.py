from datetime import datetime
import time
import uuid
from typing import Dict, List, Optional, Any
from schemas.cookie_schema import CookieSubmissionRequest, ComplianceAnalysisResult
from loguru import logger
from clients.internal_api_client import InternalAPIClient, APIConfig, AnalysisPhase, PolicyAnalysisError
import httpx # Keep httpx for type hinting in methods

# Service Layer
class PolicyAnalysisService:
    def __init__(self, api_client: InternalAPIClient):
        self.api_client = api_client

    async def discover_policy(self, client: httpx.AsyncClient, website_url: str, request_id: str) -> Dict[str, Any]:
        """Phase 1: Policy Discovery"""
        return await self.api_client.post(
            client=client,
            endpoint="/policy/discover",
            payload={"website_url": website_url},
            phase=AnalysisPhase.DISCOVERY,
            request_id=request_id
        )

    async def extract_content(
        self,
        client: httpx.AsyncClient,
        website_url: str,
        policy_url: str,
        request_id: str
    ) -> Dict[str, Any]:
        """Phase 2: Policy Content Extraction"""
        return await self.api_client.post(
            client=client,
            endpoint="/policy/extract",
            payload={
                "website_url": website_url,
                "policy_url": policy_url
            },
            phase=AnalysisPhase.EXTRACTION,
            request_id=request_id
        )

    async def extract_features(
        self,
        client: httpx.AsyncClient,
        policy_content: Dict[str, Any],
        request_id: str
    ) -> Dict[str, Any]:
        """Phase 3: Feature Extraction"""
        # Prepare content based on language detection
        if policy_content.get("detected_language") != "en":
            payload = {
                "policy_content": policy_content["translated_content"],
                "table_content": policy_content["translated_table_content"]
            }
        else:
            payload = {
                "policy_content": policy_content["original_content"],
                "table_content": str(policy_content["table_content"])
            }

        return await self.api_client.post(
            client=client,
            endpoint="/cookies/extract-features",
            payload=payload,
            phase=AnalysisPhase.FEATURE_EXTRACTION,
            request_id=request_id
        )

    async def check_compliance(
        self,
        client: httpx.AsyncClient,
        website_url: str,
        policy_features: Dict[str, Any],
        cookies: List[Dict[str, Any]],
        request_id: str
    ) -> Dict[str, Any]:
        """Phase 4: Compliance Check"""
        return await self.api_client.post(
            client=client,
            endpoint="/violations/detect",
            payload={
                "website_url": website_url,
                "policy_json": policy_features,
                "cookies": cookies
            },
            phase=AnalysisPhase.COMPLIANCE_CHECK,
            request_id=request_id
        )

    async def orchestrate_analysis(self, payload: CookieSubmissionRequest, request_id: str) -> ComplianceAnalysisResult:
        """
        Optimized policy analysis with parallel processing, proper error handling,
        and comprehensive logging.
        """
        start_time = time.time() # Keep start_time here for execution_time calculation

        logger.info(
            "analysis_started",
            request_id=request_id,
            website_url=payload.website_url,
            cookies_count=len(payload.cookies)
        )

        try:
            async with self.api_client.get_client() as client:
                # Phase 1: Policy Discovery (must be first)
                logger.info("phase_started", phase="discovery", request_id=request_id)
                discovery = await self.discover_policy(client, payload.website_url, request_id)
                logger.info("phase_completed", phase="discovery", request_id=request_id)

                policy_features = {"is_specific": 0, "cookies": []}

                if discovery.get("policy_url"):
                    logger.info("policy_url_found",
                                 policy_url=discovery["policy_url"],
                                 request_id=request_id)

                    # Phase 2 & 3: Can be optimized with parallel execution in some cases
                    # But since Phase 3 depends on Phase 2, we keep them sequential
                    logger.info("phase_started", phase="extraction", request_id=request_id)

                    policy_content = await self.extract_content(
                        client,
                        discovery["website_url"],
                        discovery["policy_url"],
                        request_id
                    )
                    logger.info("phase_completed", phase="extraction", request_id=request_id)

                    # Phase 3: Feature Extraction
                    logger.info("phase_started", phase="feature_extraction", request_id=request_id)
                    policy_features = await self.extract_features(client, policy_content, request_id)
                    logger.info("phase_completed", phase="feature_extraction", request_id=request_id)
                else:
                    logger.info("no_policy_found",
                                 website_url=payload.website_url,
                                 request_id=request_id)

                # Phase 4: Compliance Check
                logger.info("phase_started", phase="compliance_check", request_id=request_id)
                result = await self.check_compliance(
                    client,
                    payload.website_url,
                    policy_features,
                    payload.cookies,
                    request_id
                )
                logger.info("phase_completed", phase="compliance_check", request_id=request_id)

                # Calculate execution time
                execution_time = time.time() - start_time

                # Log comprehensive results
                logger.info(
                    "analysis_completed",
                    request_id=request_id,
                    total_issues=result['total_issues'],
                    compliance_score=result['compliance_score'],
                    execution_time=execution_time,
                    policy_cookies_count=result['policy_cookies_count'],
                    actual_cookies_count=result['actual_cookies_count']
                )

                # Create structured result
                analysis_result = ComplianceAnalysisResult(
                    website_url=payload.website_url,
                    analysis_date=datetime.now(),
                    total_issues=result['total_issues'],
                    compliance_score=result['compliance_score'],
                    policy_cookies_count=result['policy_cookies_count'],
                    actual_cookies_count=result['actual_cookies_count'],
                    statistics=result['statistics'],
                    issues=result['issues'],
                    summary=result['summary']
                )

                return analysis_result

        except PolicyAnalysisError as e:
            logger.error(
                "analysis_failed",
                request_id=request_id,
                phase=e.phase.value,
                error=e.message,
                status_code=e.status_code,
                execution_time=time.time() - start_time
            )
            raise e # Re-raise the custom exception
        except Exception as e:
            logger.error(
                "analysis_unexpected_error",
                request_id=request_id,
                error=str(e),
                execution_time=time.time() - start_time
            )
            raise e # Re-raise the exception
