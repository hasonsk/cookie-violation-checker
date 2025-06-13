from datetime import datetime
import json
import time
from typing import Dict, List, Optional, Any
from loguru import logger

from src.schemas.policy import PolicyContent, PolicyDiscoveryResult
from src.schemas.cookie import CookieSubmissionRequest
from src.schemas.violation import ComplianceAnalysisResponse

from src.services.policy_crawler_service.policy_crawler_service import PolicyCrawlerService
from src.services.llm_services.policy_llm_service import PolicyLLMService
from src.services.comparator_service.comparator_service import ComparatorService
from src.repositories.violation_repository import ViolationRepository

class ViolationAnalyzerService:
    def __init__(
        self,
        policy_crawler: PolicyCrawlerService,
        policy_extractor_service: PolicyLLMService,
        comparator_service: ComparatorService,
        violation_repository: ViolationRepository
    ):
        self.policy_crawler = policy_crawler
        self.policy_extractor_service = policy_extractor_service
        self.comparator_service = comparator_service
        self.violation_repository = violation_repository

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

        policy_url: Optional[str] = None # Initialize policy_url here
        try:
            # Phase 1: Policy Discovery and Content Extraction
            logger.info("phase_started", phase="policy_extraction", request_id=request_id)
            policy_content: Optional[PolicyContent] = await self.policy_crawler.extract_policy(payload.website_url)

            if policy_content and policy_content.original_content:
                logger.info("policy_content_extracted", website_url=payload.website_url, request_id=request_id)
                policy_url = policy_content.policy_url # Get policy_url from the extracted object
            else:
                logger.info("no_policy_found", website_url=payload.website_url, request_id=request_id)
                policy_url = None # Ensure policy_url is None if no content
            logger.info("phase_completed", phase="policy_crawling", request_id=request_id)

            policy_features = {"is_specific": 0, "cookies": []}

            # Phase 2: Feature Extraction (if policy content exists)
            if policy_content:
                logger.info("phase_started", phase="feature_extraction", request_id=request_id)
                if policy_content.detected_language == "en":
                    table_content_str = json.dumps(policy_content.table_content, ensure_ascii=False) if policy_content.table_content else None
                    policy_features_obj = await self.policy_extractor_service.extract_cookie_features(
                        policy_content.original_content,
                        table_content_str,
                    )
                else:
                    policy_features_obj = await self.policy_extractor_service.extract_cookie_features(
                        policy_content.translated_content,
                        policy_content.translated_table_content,
                    )
                # Convert PolicyCookieList object to a dictionary for ComparatorService
                policy_features = {
                    "is_specific": policy_features_obj.is_specific,
                    "cookies": [cookie.dict() for cookie in policy_features_obj.cookies]
                }
                logger.info("phase_completed", phase="feature_extraction", request_id=request_id)

            # Phase 3: Compliance Check
            logger.info("phase_started", phase="compliance_check", request_id=request_id)
            result = await self.comparator_service.analyze_website_compliance(
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
            await self.violation_repository.create_violation(analysis_result.dict())
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
