from datetime import datetime
import json
import time
from typing import Dict, List, Optional, Any
from loguru import logger

from src.utils.url_utils import get_base_url
from src.schemas.policy import PolicyContent
from src.schemas.cookie import CookieSubmissionRequest, PolicyCookieList
from src.schemas.violation import ComplianceAnalysisResponse
from src.models.website import Website # Giả sử model Website của bạn ở đây

from src.services.policy_crawler_service.policy_crawler_service import PolicyCrawlerService
from src.services.cookie_extractor_service.policy_cookie_extractor_service import CookieExtractorService
from src.services.comparator_service.comparator_service import ComparatorService
from src.repositories.violation_repository import ViolationRepository
from src.repositories.website_repository import WebsiteRepository # Bổ sung repository

class ViolationAnalyzerService:
    def __init__(
        self,
        policy_crawler: PolicyCrawlerService,
        policy_cookie_extractor_service: CookieExtractorService,
        comparator_service: ComparatorService,
        violation_repository: ViolationRepository,
        website_repository: WebsiteRepository # Inject WebsiteRepository
    ):
        self.policy_crawler = policy_crawler
        self.policy_cookie_extractor_service = policy_cookie_extractor_service
        self.comparator_service = comparator_service
        self.violation_repository = violation_repository
        self.website_repository = website_repository # Gán vào service

    async def orchestrate_analysis(self, payload: CookieSubmissionRequest, request_id: str) -> ComplianceAnalysisResponse:
        """
        Orchestrates the analysis process, starting with a database check to avoid re-crawling.
        """
        start_time = time.time()
        logger.info(
            "analysis_started",
            request_id=request_id,
            website_url=payload.website_url,
        )

        root_url = get_base_url(payload.website_url)
        policy_url: Optional[str] = None
        policy_features: Dict[str, Any] = {"is_specific": 0, "cookies": []}

        try:
            # === BƯỚC KIỂM TRA DATABASE ĐẦU TIÊN ===
            found_website: Optional[Website] = await self.website_repository.get_website_by_root_url(root_url)

            if found_website:
                # CACHE HIT: Website đã có trong DB
                logger.info("website_found_in_db", website_url=root_url, request_id=request_id)

                # Lấy thông tin đã lưu, bỏ qua crawling và feature extraction
                policy_url = found_website.policy_url
                policy_features = {
                    "is_specific": found_website.is_specific,
                    "cookies": [cookie.dict() for cookie in found_website.policy_cookies]
                }

                # Cập nhật thời gian quét
                await self.website_repository.update_website(found_website.id, {"last_checked_at": datetime.utcnow()})
                logger.info("phase_skipped", phases=["policy_extraction", "feature_extraction"], request_id=request_id)

            else:
                # CACHE MISS: Website mới, thực hiện quy trình đầy đủ
                logger.info("website_not_found_in_db", website_url=root_url, request_id=request_id)

                # Phase 1: Policy Discovery and Content Extraction
                logger.info("phase_started", phase="policy_extraction", request_id=request_id)
                policy_content: Optional[PolicyContent] = await self.policy_crawler.extract_policy(payload.website_url)
                if policy_content:
                    policy_url = policy_content.policy_url

                # Phase 2: Feature Extraction
                policy_features_obj = None
                if policy_content and policy_content.original_content:
                    logger.info("phase_started", phase="feature_extraction", request_id=request_id)
                    # (logic trích xuất feature của bạn ở đây)
                    policy_features_obj = await self.policy_cookie_extractor_service.extract_cookie_features(
                        policy_content.original_content,
                        json.dumps(policy_content.table_content, ensure_ascii=False) if policy_content.table_content else None,
                    )
                    policy_features = {
                        "is_specific": policy_features_obj.is_specific,
                        "cookies": [cookie.dict() for cookie in policy_features_obj.cookies]
                    }

                # === FIX: Chuyển đổi list object thành list dictionary ===
                policy_cookies_for_db = []
                if policy_features_obj and policy_features_obj.cookies:
                    policy_cookies_for_db = [cookie.model_dump() for cookie in policy_features_obj.cookies]
                # =======================================================

                # Lưu website mới vào DB để tái sử dụng lần sau
                new_website_data = {
                    "domain": root_url,
                    "provider_id": None, # Hoặc provider_id nếu có
                    "last_checked_at": datetime.utcnow(),
                    "policy_url": policy_url,
                    "detected_language": policy_content.detected_language if policy_content else None,
                    "original_content": policy_content.original_content if policy_content else "",
                    "translated_content": policy_content.translated_content if policy_content else None,
                    "table_content": policy_content.table_content if policy_content else [],
                    "translated_table_content": policy_content.translated_table_content if policy_content else None,
                    "is_specific": policy_features_obj.is_specific if policy_features_obj else 0,
                    "policy_cookies": policy_cookies_for_db # <-- SỬ DỤNG LIST DICTIONARY Ở ĐÂY
                }
                await self.website_repository.create_website(new_website_data)
                logger.info("new_website_saved_to_db", website_url=root_url, request_id=request_id)

            # === BƯỚC PHÂN TÍCH VÀ LƯU TRỮ (DÙNG CHUNG CHO CẢ 2 LUỒNG) ===
            logger.info("phase_started", phase="compliance_check", request_id=request_id)
            result = await self.comparator_service.compare_compliance(
                payload.website_url,
                payload.cookies,
                policy_features,
            )

            # (Phần còn lại của hàm giữ nguyên)
            # ...

            # Save the analysis result to the database
            await self.violation_repository.create_violation(result.model_dump())
            logger.info("Analysis result saved to database", request_id=request_id)

            # Return response
            return ComplianceAnalysisResponse(**result.model_dump(), policy_url=policy_url)

        except Exception as e:
            logger.error(
                "analysis_unexpected_error",
                request_id=request_id,
                error=str(e),
                execution_time=time.time() - start_time
            )
            raise e
