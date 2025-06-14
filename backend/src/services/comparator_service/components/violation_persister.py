from loguru import logger

from src.schemas.violation import ComplianceAnalysisResult
from src.services.comparator_service.interfaces.violation_persister import IViolationPersister


class ViolationPersister(IViolationPersister):
    """Chuyên lưu trữ violation - FUNCTIONAL COHESION"""

    def __init__(self, violation_repository):
        self._violation_repository = violation_repository

    async def save_violation(self, result: ComplianceAnalysisResult) -> bool:
        """Chỉ làm 1 việc: lưu violation result"""
        try:
            # Convert Pydantic models to dict for MongoDB
            violation_data = result.model_dump()
            violation_data['issues'] = [issue.model_dump() if hasattr(issue, 'model_dump') else issue
                                      for issue in violation_data['issues']]

            await self._violation_repository.create_violation(violation_data)
            return True
        except Exception as e:
            logger.error(f"Failed to save violation: {str(e)}")
            return False
