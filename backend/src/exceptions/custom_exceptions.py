from src.schemas.violation import AnalysisPhase
from fastapi import HTTPException, status

# Auth-related
class EmailAlreadyExistsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Email đã tồn tại")

class InvalidCredentialsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Thông tin đăng nhập không chính xác")

class UnauthorizedError(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Token không hợp lệ hoặc đã hết hạn")

class UserNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Người dùng không tồn tại")

# Analyze-related
class PolicyDiscoveryError(HTTPException):
    def __init__(self, status_code: int = 500):
        super().__init__(status_code=status_code, detail="Không thể phát hiện chính sách cookie")

class PolicyExtractionError(HTTPException):
    def __init__(self, status_code: int = 500):
        super().__init__(status_code=status_code, detail="Không thể trích xuất nội dung chính sách")

class FeatureExtractionError(HTTPException):
    def __init__(self, status_code: int = 500):
        super().__init__(status_code=status_code, detail="Không thể trích xuất đặc trưng từ chính sách")

class ComplianceCheckError(HTTPException):
    def __init__(self, status_code: int = 500):
        super().__init__(status_code=status_code, detail="Không thể kiểm tra tuân thủ cookie")

class PolicyAnalysisError(Exception):
    def __init__(self, phase: AnalysisPhase, message: str, status_code: int = 500):
        self.phase = phase
        self.message = message
        self.status_code = status_code
        super().__init__(f"[{phase.value}] {message}")

class RetryableError(Exception):
    pass
