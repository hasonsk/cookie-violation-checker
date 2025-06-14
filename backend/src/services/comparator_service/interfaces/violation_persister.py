from abc import ABC, abstractmethod

from src.schemas.violation import ComplianceAnalysisResult

class IViolationPersister(ABC):
    """Interface để lưu trữ violation"""

    @abstractmethod
    async def save_violation(self, result: ComplianceAnalysisResult) -> bool:
        """Lưu kết quả violation"""
        pass
