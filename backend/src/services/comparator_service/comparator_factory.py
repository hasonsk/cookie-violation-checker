from src.services.comparator_service.comparator_service import ComparatorService
from src.services.comparator_service.components.compliance_analyzer import ComplianceAnalyzer
from src.services.comparator_service.components.compliance_result import ComplianceResultBuilder
from src.services.comparator_service.components.cookie_data_processor import CookieDataProcessor
from src.services.comparator_service.components.violation_persister import ViolationPersister


class ComparatorFactory:
    """Factory để tạo orchestrator với tất cả dependencies"""

    @staticmethod
    def create_comparator(violation_repository, violation_analyzer) -> ComparatorService:
        """Tạo orchestrator với tất cả dependencies được inject"""

        from src.utils.cookie_utils import extract_main_domain

        cookie_processor = CookieDataProcessor()
        compliance_analyzer = ComplianceAnalyzer(violation_analyzer)
        result_builder = ComplianceResultBuilder()
        violation_persister = ViolationPersister(violation_repository)

        return ComparatorService(
            cookie_processor=cookie_processor,
            compliance_analyzer=compliance_analyzer,
            result_builder=result_builder,
            violation_persister=violation_persister,
            domain_extractor=extract_main_domain
        )
