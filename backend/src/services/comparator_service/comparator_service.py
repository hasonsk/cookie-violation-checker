from typing import Dict, List, Optional
from loguru import logger

from src.schemas.violation import ComplianceAnalysisResult
from src.services.comparator_service.interfaces.compliance_analyzer import IComplianceAnalyzer
from src.services.comparator_service.interfaces.compliance_result import IComplianceResultBuilder
from src.services.comparator_service.interfaces.cookie_data_processor import ICookieDataProcessor
from src.services.comparator_service.interfaces.violation_persister import IViolationPersister


class ComparatorService:
    """
    Orchestrator chỉ làm 1 việc: điều phối quá trình phân tích compliance
    Sequential Cohesion - output của bước trước là input của bước sau
    """

    def __init__(
        self,
        cookie_processor: ICookieDataProcessor,
        compliance_analyzer: IComplianceAnalyzer,
        result_builder: IComplianceResultBuilder,
        violation_persister: IViolationPersister,
        domain_extractor
    ):
        self._cookie_processor = cookie_processor
        self._compliance_analyzer = compliance_analyzer
        self._result_builder = result_builder
        self._violation_persister = violation_persister
        self._domain_extractor = domain_extractor

    async def compare_compliance(
        self,
        website_url: str,
        cookies: List[Dict],
        policy_json: Optional[Dict] = None
    ) -> ComplianceAnalysisResult:
        """
        Sequential process:
        1. Extract domain -> 2. Process cookies -> 3. Analyze -> 4. Build result -> 5. Save
        """

        try:
            # Step 1: Extract domain
            main_domain = self._domain_extractor(website_url)

            # Step 2: Process cookies (output: processed cookies)
            policy_cookies = self._cookie_processor.process_policy_cookies(
                policy_json or {"cookies": []}
            )
            actual_cookies = self._cookie_processor.process_actual_cookies(cookies)

            # Step 3: Analyze compliance (input: processed cookies, output: analysis result)
            analysis_data = self._compliance_analyzer.analyze(
                policy_cookies, actual_cookies, main_domain
            )

            # Check for analysis errors
            if "error" in analysis_data and analysis_data["error"]:
                result = self._result_builder.build_error_result(
                    website_url, analysis_data["error"]
                )
                return result

            # Step 4: Build result (input: analysis data, output: compliance result)
            result = self._result_builder.build_success_result(website_url, analysis_data)

            # Step 5: Save result (input: compliance result)
            await self._violation_persister.save_violation(result)

            return result

        except Exception as e:
            logger.error(f"Compliance analysis failed for {website_url}: {str(e)}")
            return self._result_builder.build_error_result(website_url, str(e))
