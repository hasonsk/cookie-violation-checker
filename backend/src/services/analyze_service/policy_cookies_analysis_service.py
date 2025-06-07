from datetime import datetime
import json
import time
from schemas.policy_schema import PolicyContent, PolicyDiscoveryResult
from typing import Dict, List, Optional, Any
from schemas.cookie_schema import CookieSubmissionRequest, ComplianceAnalysisResponse
from loguru import logger

from services.policy_discover_service.policy_discovery_service import PolicyDiscoveryService
from services.policy_extract_service.policy_extract_service import PolicyExtractService
from services.cookies_extract_service.cookies_extractor import CookieExtractorService
from services.violation_detect_service.violation_detector_service import ViolationDetectorService
from repositories.violation_repo import ViolationRepository # Add this import

class PolicyCookiesAnalysisService:
    def __init__(
        self,
        discovery_service: PolicyDiscoveryService,
        extract_service: PolicyExtractService,
        feature_service: CookieExtractorService,
        violation_service: ViolationDetectorService,
        violation_repo: ViolationRepository
    ):
        self.discovery_service = discovery_service
        self.extract_service = extract_service
        self.feature_service = feature_service
        self.violation_service = violation_service
        self.violation_repo = violation_repo

    async def orchestrate_analysis(self, payload: CookieSubmissionRequest, request_id: str) -> ComplianceAnalysisResponse:
        """
        Optimized policy analysis with parallel processing, proper error handling,
        and comprehensive logging.
        """
        start_time = time.time()

        logger.info(
            "analysis_started",
            request_id=request_id,
            website_url=payload.website_url,
            cookies_count=len(payload.cookies)
        )

        policy_url = None
        try:
            # Phase 1: Policy Discovery
            logger.info("phase_started", phase="discovery", request_id=request_id)
            discovery_result: PolicyDiscoveryResult = await self.discovery_service.find_policy_url(payload.website_url)
            logger.info("phase_completed", phase="discovery", request_id=request_id)

            policy_features = {"is_specific": 0, "cookies": []}
            policy_url = discovery_result.policy_url

            if policy_url:
                logger.info("policy_url_found",
                             policy_url=policy_url,
                             request_id=request_id)

                # Phase 2: Policy Content Extraction
                logger.info("phase_started", phase="extraction", request_id=request_id)
                async with self.extract_service as extractor:
                    policy_content = await extractor.extract_policy_content(
                        website_url=discovery_result.website_url,
                        policy_url=policy_url
                    )
                logger.info("phase_completed", phase="extraction", request_id=request_id)
                logger.warning(policy_content) # Consider removing this warning in production

                # Phase 3: Feature Extraction
                logger.info("phase_started", phase="feature_extraction", request_id=request_id)
                if policy_content.detected_language == "en":
                    policy_features_obj = await self.feature_service.extract_cookie_features(
                        policy_content.original_content,
                        policy_content.table_content,
                    )
                else:
                    policy_features_obj = await self.feature_service.extract_cookie_features(
                        policy_content.translated_content,
                        policy_content.translated_table_content,
                    )
                # Convert PolicyCookieList object to a dictionary for ViolationDetectorService
                policy_features = {
                    "is_specific": policy_features_obj.is_specific,
                    "cookies": [cookie.dict() for cookie in policy_features_obj.cookies]
                }
                logger.info("phase_completed", phase="feature_extraction", request_id=request_id)
            else:
                logger.info("no_policy_found",
                             website_url=payload.website_url,
                             request_id=request_id)

            # Phase 4: Compliance Check
            logger.info("phase_started", phase="compliance_check", request_id=request_id)
            result = await self.violation_service.analyze_website_compliance(
                payload.website_url,
                payload.cookies,
                policy_features,
            )
            logger.info("phase_completed", phase="compliance_check", request_id=request_id)

            # Calculate execution time
            execution_time = time.time() - start_time

            # Log comprehensive results
            logger.info(
                "analysis_completed",
                request_id=request_id,
                total_issues=result.total_issues,
                compliance_score=result.compliance_score,
                execution_time=execution_time,
                policy_cookies_count=result.policy_cookies_count,
                actual_cookies_count=result.actual_cookies_count
            )

            # Create structured result
            analysis_result = ComplianceAnalysisResponse(
                website_url=payload.website_url,
                policy_url=policy_url,
                analysis_date=datetime.now(),
                total_issues=result.total_issues,
                compliance_score=result.compliance_score,
                policy_cookies_count=result.policy_cookies_count,
                actual_cookies_count=result.actual_cookies_count,
                statistics=result.statistics,
                issues=result.issues,
                summary=result.summary,
                details=result.details
            )
            logger.debug(f"Type of analysis_result before return: {type(analysis_result)}")

            # Save the analysis result to the database
            await self.violation_repo.create_violation(analysis_result.dict())
            logger.info("Analysis result saved to database", request_id=request_id)

            return analysis_result

        except Exception as e:
            logger.error(
                "analysis_unexpected_error",
                request_id=request_id,
                error=str(e),
                execution_time=time.time() - start_time
            )
            raise e
