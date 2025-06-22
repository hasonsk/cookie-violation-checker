import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
import json
from bson import ObjectId # Import ObjectId

from src.services.violation_analyzer_service.violation_analyzer_service import ViolationAnalyzerService
from src.services.policy_crawler_service.policy_crawler_service import PolicyCrawlerService
from src.services.cookie_extractor_service.policy_cookie_extractor_service import CookieExtractorService
from src.services.comparator_service.comparator_service import ComparatorService
from src.repositories.violation_repository import ViolationRepository
from src.repositories.website_repository import WebsiteRepository
from src.schemas.cookie import CookieSubmissionRequest, PolicyCookieList, PolicyCookie
from src.schemas.policy import PolicyContent
from src.schemas.violation import ComplianceAnalysisResult, ComplianceAnalysisResponse, ComplianceIssue
from src.models.website import Website
from src.utils.url_utils import get_base_url

# Mock data
MOCK_WEBSITE_URL = "https://example.com"
MOCK_ROOT_URL = get_base_url(MOCK_WEBSITE_URL)
MOCK_REQUEST_ID = "test_request_123"
MOCK_ACTUAL_COOKIES = [{
    "name": "test_cookie",
    "value": "123",
    "domain": "example.com",
    "expirationDate": "2025-12-31T23:59:59Z", # Added missing field
    "secure": True, # Added missing field
    "httpOnly": False, # Added missing field
    "sameSite": "Lax" # Added missing field
}]
MOCK_POLICY_URL = "https://example.com/privacy-policy"
MOCK_POLICY_CONTENT_TEXT = "This is a cookie policy. It mentions test_cookie."
MOCK_POLICY_COOKIES_LIST = PolicyCookieList(
    is_specific=1,
    cookies=[
        PolicyCookie(
            cookie_name="test_cookie",
            declared_purpose="testing",
            declared_retention="session",
            declared_third_parties=[],
            declared_description="A test cookie for internal use."
        )
    ]
)
MOCK_COMPLIANCE_RESULT = ComplianceAnalysisResult(
    website_url=MOCK_WEBSITE_URL,
    issues=[
        ComplianceIssue(
            issue_id=1,
            category="Cookie Compliance",
            type="missing_in_policy",
            description="Cookie 'test_cookie' found on website but not declared in policy.",
            severity="High",
            cookie_name="test_cookie",
            details={}
        )
    ],
    compliance_score=50,
    analysis_date=datetime.utcnow(),
    total_issues=1,
    statistics={},
    summary={},
    policy_cookies_count=0,
    actual_cookies_count=1,
    details={}
)

@pytest.fixture
def mock_policy_crawler():
    return AsyncMock(spec=PolicyCrawlerService)

@pytest.fixture
def mock_cookie_extractor_service():
    return AsyncMock(spec=CookieExtractorService)

@pytest.fixture
def mock_comparator_service():
    return AsyncMock(spec=ComparatorService)

@pytest.fixture
def mock_violation_repository():
    return AsyncMock(spec=ViolationRepository)

@pytest.fixture
def mock_website_repository():
    return AsyncMock(spec=WebsiteRepository)

@pytest.fixture
def violation_analyzer_service(
    mock_policy_crawler,
    mock_cookie_extractor_service,
    mock_comparator_service,
    mock_violation_repository,
    mock_website_repository
):
    return ViolationAnalyzerService(
        policy_crawler=mock_policy_crawler,
        policy_cookie_extractor_service=mock_cookie_extractor_service,
        comparator_service=mock_comparator_service,
        violation_repository=mock_violation_repository,
        website_repository=mock_website_repository
    )

@pytest.mark.asyncio
async def test_orchestrate_analysis_new_website_success(
    violation_analyzer_service,
    mock_policy_crawler,
    mock_cookie_extractor_service,
    mock_comparator_service,
    mock_violation_repository,
    mock_website_repository
):
    """
    Test the full analysis flow for a new website (cache miss).
    """
    # Mock repository responses
    mock_website_repository.get_website_by_root_url.return_value = None
    mock_policy_crawler.extract_policy.return_value = PolicyContent(
        website_url=MOCK_ROOT_URL,
        policy_url=MOCK_POLICY_URL,
        original_content=MOCK_POLICY_CONTENT_TEXT,
        table_content=[],
        detected_language="en",
        translated_content=None,
        translated_table_content=None
    )
    mock_cookie_extractor_service.extract_cookie_features.return_value = MOCK_POLICY_COOKIES_LIST
    mock_comparator_service.compare_compliance.return_value = MOCK_COMPLIANCE_RESULT
    mock_website_repository.create_website.return_value = Website(
        id=ObjectId(), # Use ObjectId
        domain=MOCK_ROOT_URL,
        company_name=None, # Added missing field
        provider_id=None,
        policy_url=MOCK_POLICY_URL,
        is_specific=MOCK_POLICY_COOKIES_LIST.is_specific,
        policy_cookies=[cookie.model_dump() for cookie in MOCK_POLICY_COOKIES_LIST.cookies],
        last_checked_at=datetime.utcnow(), # Changed to last_checked_at
        detected_language="en",
        original_content=MOCK_POLICY_CONTENT_TEXT,
        translated_content=None,
        table_content=[],
        translated_table_content=None
    )
    mock_violation_repository.create_violation.return_value = None # No specific return needed

    payload = CookieSubmissionRequest(
        website_url=MOCK_WEBSITE_URL,
        cookies=MOCK_ACTUAL_COOKIES
    )

    response = await violation_analyzer_service.orchestrate_analysis(payload, MOCK_REQUEST_ID)

    # Assertions
    mock_website_repository.get_website_by_root_url.assert_called_once_with(MOCK_ROOT_URL)
    mock_policy_crawler.extract_policy.assert_called_once_with(MOCK_WEBSITE_URL)
    mock_cookie_extractor_service.extract_cookie_features.assert_called_once()
    mock_website_repository.create_website.assert_called_once()
    mock_comparator_service.compare_compliance.assert_called_once()
    mock_violation_repository.create_violation.assert_called_once()

    assert response.website_url == MOCK_WEBSITE_URL
    assert response.policy_url == MOCK_POLICY_URL
    assert response.compliance_score == MOCK_COMPLIANCE_RESULT.compliance_score
    assert len(response.issues) == len(MOCK_COMPLIANCE_RESULT.issues)
    assert response.issues[0].cookie_name == MOCK_COMPLIANCE_RESULT.issues[0].cookie_name

@pytest.mark.asyncio
async def test_orchestrate_analysis_existing_website_cache_hit(
    violation_analyzer_service,
    mock_policy_crawler,
    mock_cookie_extractor_service,
    mock_comparator_service,
    mock_violation_repository,
    mock_website_repository
):
    """
    Test the analysis flow for an existing website (cache hit).
    """
    existing_website = Website(
        id=ObjectId(), # Use ObjectId
        domain=MOCK_ROOT_URL,
        company_name=None, # Added missing field
        provider_id=None,
        policy_url=MOCK_POLICY_URL,
        is_specific=MOCK_POLICY_COOKIES_LIST.is_specific,
        policy_cookies=[cookie.model_dump() for cookie in MOCK_POLICY_COOKIES_LIST.cookies],
        last_checked_at=datetime.utcnow(), # Changed to last_checked_at
        detected_language="en",
        original_content=MOCK_POLICY_CONTENT_TEXT,
        translated_content=None,
        table_content=[],
        translated_table_content=None
    )
    mock_website_repository.get_website_by_root_url.return_value = existing_website
    mock_website_repository.update_website.return_value = None
    mock_comparator_service.compare_compliance.return_value = MOCK_COMPLIANCE_RESULT
    mock_violation_repository.create_violation.return_value = None

    payload = CookieSubmissionRequest(
        website_url=MOCK_WEBSITE_URL,
        cookies=MOCK_ACTUAL_COOKIES
    )

    response = await violation_analyzer_service.orchestrate_analysis(payload, MOCK_REQUEST_ID)

    # Assertions
    mock_website_repository.get_website_by_root_url.assert_called_once_with(MOCK_ROOT_URL)
    mock_website_repository.update_website.assert_called_once()
    mock_policy_crawler.extract_policy.assert_not_called() # Should be skipped
    mock_cookie_extractor_service.extract_cookie_features.assert_not_called() # Should be skipped
    mock_website_repository.create_website.assert_not_called() # Should be skipped
    mock_comparator_service.compare_compliance.assert_called_once()
    mock_violation_repository.create_violation.assert_called_once()

    assert response.website_url == MOCK_WEBSITE_URL
    assert response.policy_url == MOCK_POLICY_URL
    assert response.compliance_score == MOCK_COMPLIANCE_RESULT.compliance_score

@pytest.mark.asyncio
async def test_orchestrate_analysis_policy_not_found(
    violation_analyzer_service,
    mock_policy_crawler,
    mock_cookie_extractor_service,
    mock_comparator_service,
    mock_violation_repository,
    mock_website_repository
):
    """
    Test the analysis flow when policy cannot be found.
    """
    mock_website_repository.get_website_by_root_url.return_value = None
    mock_policy_crawler.extract_policy.return_value = None # Policy not found
    mock_comparator_service.compare_compliance.return_value = MOCK_COMPLIANCE_RESULT # Still call comparator with empty policy
    mock_violation_repository.create_violation.return_value = None

    payload = CookieSubmissionRequest(
        website_url=MOCK_WEBSITE_URL,
        cookies=MOCK_ACTUAL_COOKIES
    )

    response = await violation_analyzer_service.orchestrate_analysis(payload, MOCK_REQUEST_ID)

    # Assertions
    mock_website_repository.get_website_by_root_url.assert_called_once_with(MOCK_ROOT_URL)
    mock_policy_crawler.extract_policy.assert_called_once_with(MOCK_WEBSITE_URL)
    mock_cookie_extractor_service.extract_cookie_features.assert_not_called() # Should be skipped
    mock_website_repository.create_website.assert_not_called() # Should be skipped
    mock_comparator_service.compare_compliance.assert_called_once() # Should still be called
    mock_violation_repository.create_violation.assert_called_once()

    assert response.website_url == MOCK_WEBSITE_URL
    assert response.policy_url is None # Policy URL should be None
    assert response.compliance_score == MOCK_COMPLIANCE_RESULT.compliance_score

@pytest.mark.asyncio
async def test_orchestrate_analysis_extraction_failure(
    violation_analyzer_service,
    mock_policy_crawler,
    mock_cookie_extractor_service,
    mock_comparator_service,
    mock_violation_repository,
    mock_website_repository
):
    """
    Test the analysis flow when cookie extraction fails.
    """
    mock_website_repository.get_website_by_root_url.return_value = None
    mock_policy_crawler.extract_policy.return_value = PolicyContent(
        website_url=MOCK_ROOT_URL,
        policy_url=MOCK_POLICY_URL,
        original_content=MOCK_POLICY_CONTENT_TEXT,
        table_content=[],
        detected_language="en",
        translated_content=None,
        translated_table_content=None
    )
    mock_cookie_extractor_service.extract_cookie_features.return_value = PolicyCookieList(is_specific=0, cookies=[]) # Empty list on failure
    mock_comparator_service.compare_compliance.return_value = MOCK_COMPLIANCE_RESULT
    mock_violation_repository.create_violation.return_value = None

    payload = CookieSubmissionRequest(
        website_url=MOCK_WEBSITE_URL,
        cookies=MOCK_ACTUAL_COOKIES
    )

    response = await violation_analyzer_service.orchestrate_analysis(payload, MOCK_REQUEST_ID)

    # Assertions
    mock_website_repository.get_website_by_root_url.assert_called_once_with(MOCK_ROOT_URL)
    mock_policy_crawler.extract_policy.assert_called_once_with(MOCK_WEBSITE_URL)
    mock_cookie_extractor_service.extract_cookie_features.assert_called_once()
    mock_website_repository.create_website.assert_called_once() # Website still saved, but with empty policy_cookies
    mock_comparator_service.compare_compliance.assert_called_once()
    mock_violation_repository.create_violation.assert_called_once()

    assert response.website_url == MOCK_WEBSITE_URL
    assert response.policy_url == MOCK_POLICY_URL
    assert response.compliance_score == MOCK_COMPLIANCE_RESULT.compliance_score
    # Ensure that the comparator was called with an empty policy_features cookies list
    args, kwargs = mock_comparator_service.compare_compliance.call_args
    assert kwargs['policy_json']['cookies'] == []
