from fastapi import APIRouter
from typing import List
from schemas.cookie_schema import Cookie, CookieSubmissionResponse
from controllers.violation_detect_controller import ViolationDetectorController

router = APIRouter(prefix="", tags=["cookies"])
controller = ViolationDetectorController()

@router.post("/submit-cookies", response_model=CookieSubmissionResponse)
async def submit_cookies(cookies: List[Cookie]) -> CookieSubmissionResponse:
    """
    Endpoint để nhận và phân tích cookies từ browser extension
    """
    return await controller.submit_cookies(cookies)
