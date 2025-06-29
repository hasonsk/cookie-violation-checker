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

class DomainRequestNotFoundError(Exception):
    pass

class DomainAlreadyExistsError(Exception):
    def __init__(self, message: str = "Domain đã tồn tại trong hệ thống"):
        super().__init__(message)
class DomainRequestAlreadyExistsError(Exception):
    def __init__(self, message: str = "Yêu cầu đăng ký domain đã tồn tại"):
        super().__init__(message)
class DomainRequestRejectedError(Exception):
    def __init__(self, message: str = "Yêu cầu đăng ký domain đã bị từ chối"):
        super().__init__(message)
class DomainRequestPendingError(Exception):
    def __init__(self, message: str = "Yêu cầu đăng ký domain đang chờ phê duyệt"):
        super().__init__(message)
class DomainRequestApprovalError(Exception):
    def __init__(self, message: str = "Lỗi khi phê duyệt yêu cầu đăng ký domain"):
        super().__init__(message)
class DomainRequestRejectionError(Exception):
    def __init__(self, message: str = "Lỗi khi từ chối yêu cầu đăng ký domain"):
        super().__init__(message)
class DomainRequestNotAuthorizedError(Exception):
    def __init__(self, message: str = "Người dùng không có quyền thực hiện hành động này"):
        super().__init__(message)
class InvalidDomainError(Exception):
    def __init__(self, message: str = "Domain không hợp lệ"):
        super().__init__(message)

class NotFoundException(Exception):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)

class BadRequestException(Exception):
    def __init__(self, message: str = "Bad request"):
        super().__init__(message)

class PolicyCrawlException(Exception):
    def __init__(self, message: str = "Failed to crawl policy"):
        super().__init__(message)
