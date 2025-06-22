import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Optional

from src.services.cookie_extractor_service.policy_cookie_extractor_service import CookieExtractorService
from src.services.cookie_extractor_service.interfaces.llm_provider import ILLMProvider
from src.services.cookie_extractor_service.processors.content_analyzer import ContentAnalyzer
from src.services.cookie_extractor_service.processors.prompt_builder import PromptBuilder
from src.services.cookie_extractor_service.processors.response_processor import LLMResponseProcessor
from src.repositories.cookie_feature_repository import CookieFeatureRepository
from src.schemas.cookie import PolicyCookieList, PolicyCookie

# Mock data
MOCK_ORIGINAL_CONTENT = "This is a policy document. It mentions a cookie named 'session_id' for user tracking."
MOCK_TABLE_CONTENT = '[{"name": "analytics_id", "purpose": "analytics"}]'
MOCK_LLM_RAW_RESPONSE_SUCCESS = """
```json
{
    "is_specific": 1,
    "cookies": [
        {
            "cookie_name": "session_id",
            "declared_purpose": "user tracking",
            "declared_retention": "session",
            "declared_third_parties": [],
            "declared_description": "Tracks user session."
        },
        {
            "cookie_name": "analytics_id",
            "declared_purpose": "analytics",
            "declared_retention": "1 year",
            "declared_third_parties": ["Google"],
            "declared_description": "Used for website analytics."
        }
    ]
}
```
"""
MOCK_LLM_CLEAN_RESPONSE_SUCCESS = """
{
    "is_specific": 1,
    "cookies": [
        {
            "cookie_name": "session_id",
            "declared_purpose": "user tracking",
            "declared_retention": "session",
            "declared_third_parties": [],
            "declared_description": "Tracks user session."
        },
        {
            "cookie_name": "analytics_id",
            "declared_purpose": "analytics",
            "declared_retention": "1 year",
            "declared_third_parties": ["Google"],
            "declared_description": "Used for website analytics."
        }
    ]
}
"""
MOCK_LLM_RESPONSE_DICT_SUCCESS = {
    "is_specific": 1,
    "cookies": [
        {
            "cookie_name": "session_id",
            "declared_purpose": "user tracking",
            "declared_retention": "session",
            "declared_third_parties": [],
            "declared_description": "Tracks user session."
        },
        {
            "cookie_name": "analytics_id",
            "declared_purpose": "analytics",
            "declared_retention": "1 year",
            "declared_third_parties": ["Google"],
            "declared_description": "Used for website analytics."
        }
    ]
}
MOCK_POLICY_COOKIE_LIST_SUCCESS = PolicyCookieList(
    is_specific=1,
    cookies=[
        PolicyCookie(
            cookie_name="session_id",
            declared_purpose="user tracking",
            declared_retention="session",
            declared_third_parties=[],
            declared_description="Tracks user session."
        ),
        PolicyCookie(
            cookie_name="analytics_id",
            declared_purpose="analytics",
            declared_retention="1 year",
            declared_third_parties=["Google"],
            declared_description="Used for website analytics."
        )
    ]
)

@pytest.fixture
def mock_llm_provider():
    return AsyncMock(spec=ILLMProvider)

@pytest.fixture
def mock_content_analyzer():
    return MagicMock(spec=ContentAnalyzer)

@pytest.fixture
def mock_prompt_builder():
    return MagicMock(spec=PromptBuilder)

@pytest.fixture
def mock_response_processor():
    return MagicMock(spec=LLMResponseProcessor)

@pytest.fixture
def mock_cookie_feature_repository():
    return AsyncMock(spec=CookieFeatureRepository)

@pytest.fixture
def cookie_extractor_service(
    mock_llm_provider,
    mock_content_analyzer,
    mock_prompt_builder,
    mock_response_processor,
    mock_cookie_feature_repository
):
    return CookieExtractorService(
        llm_provider=mock_llm_provider,
        content_analyzer=mock_content_analyzer,
        prompt_builder=mock_prompt_builder,
        response_processor=mock_response_processor,
        cookie_feature_repository=mock_cookie_feature_repository
    )

@pytest.mark.asyncio
async def test_extract_cookie_features_success(
    cookie_extractor_service,
    mock_llm_provider,
    mock_content_analyzer,
    mock_prompt_builder,
    mock_response_processor,
    mock_cookie_feature_repository
):
    """
    Test successful cookie feature extraction.
    """
    mock_content_analyzer.prepare_content_for_analysis.return_value = (MOCK_ORIGINAL_CONTENT, "original")
    mock_prompt_builder.build_cookie_extraction_prompt.return_value = "Extract cookies from: " + MOCK_ORIGINAL_CONTENT
    mock_llm_provider.generate_content.return_value = MOCK_LLM_RAW_RESPONSE_SUCCESS
    mock_response_processor.clean_json_response.return_value = MOCK_LLM_CLEAN_RESPONSE_SUCCESS
    mock_response_processor.parse_json_response.return_value = MOCK_LLM_RESPONSE_DICT_SUCCESS
    mock_cookie_feature_repository.insert_many.return_value = None

    result = await cookie_extractor_service.extract_cookie_features(
        original_content=MOCK_ORIGINAL_CONTENT,
        table_content=MOCK_TABLE_CONTENT
    )

    mock_content_analyzer.prepare_content_for_analysis.assert_called_once_with(MOCK_ORIGINAL_CONTENT, MOCK_TABLE_CONTENT)
    mock_prompt_builder.build_cookie_extraction_prompt.assert_called_once()
    mock_llm_provider.generate_content.assert_called_once()
    mock_response_processor.clean_json_response.assert_called_once()
    mock_response_processor.parse_json_response.assert_called_once()
    mock_cookie_feature_repository.insert_many.assert_called_once()

    assert result == MOCK_POLICY_COOKIE_LIST_SUCCESS
    assert len(result.cookies) == 2

@pytest.mark.asyncio
async def test_extract_cookie_features_no_content(
    cookie_extractor_service,
    mock_llm_provider,
    mock_content_analyzer,
    mock_prompt_builder,
    mock_response_processor,
    mock_cookie_feature_repository
):
    """
    Test when no content is provided for extraction.
    """
    mock_content_analyzer.prepare_content_for_analysis.return_value = (None, None)

    result = await cookie_extractor_service.extract_cookie_features(
        original_content=None,
        table_content=None
    )

    mock_content_analyzer.prepare_content_for_analysis.assert_called_once_with(None, None)
    mock_prompt_builder.build_cookie_extraction_prompt.assert_not_called()
    mock_llm_provider.generate_content.assert_not_called()
    mock_response_processor.clean_json_response.assert_not_called()
    mock_response_processor.parse_json_response.assert_not_called()
    mock_cookie_feature_repository.insert_many.assert_not_called()

    assert result == PolicyCookieList(is_specific=0, cookies=[])

@pytest.mark.asyncio
async def test_extract_cookie_features_llm_error(
    cookie_extractor_service,
    mock_llm_provider,
    mock_content_analyzer,
    mock_prompt_builder,
    mock_response_processor,
    mock_cookie_feature_repository
):
    """
    Test when LLM returns an invalid response or an error occurs during LLM interaction.
    """
    mock_content_analyzer.prepare_content_for_analysis.return_value = (MOCK_ORIGINAL_CONTENT, "original")
    mock_prompt_builder.build_cookie_extraction_prompt.return_value = "Extract cookies from: " + MOCK_ORIGINAL_CONTENT
    mock_llm_provider.generate_content.side_effect = Exception("LLM API error") # Simulate LLM error

    result = await cookie_extractor_service.extract_cookie_features(
        original_content=MOCK_ORIGINAL_CONTENT,
        table_content=MOCK_TABLE_CONTENT
    )

    mock_content_analyzer.prepare_content_for_analysis.assert_called_once_with(MOCK_ORIGINAL_CONTENT, MOCK_TABLE_CONTENT)
    mock_prompt_builder.build_cookie_extraction_prompt.assert_called_once()
    mock_llm_provider.generate_content.assert_called_once()
    mock_response_processor.clean_json_response.assert_not_called() # Should not be called after LLM error
    mock_response_processor.parse_json_response.assert_not_called() # Should not be called after LLM error
    mock_cookie_feature_repository.insert_many.assert_not_called()

    assert result == PolicyCookieList(is_specific=0, cookies=[])

@pytest.mark.asyncio
async def test_extract_cookie_features_invalid_llm_response(
    cookie_extractor_service,
    mock_llm_provider,
    mock_content_analyzer,
    mock_prompt_builder,
    mock_response_processor,
    mock_cookie_feature_repository
):
    """
    Test when LLM returns a response that cannot be parsed into valid JSON.
    """
    mock_content_analyzer.prepare_content_for_analysis.return_value = (MOCK_ORIGINAL_CONTENT, "original")
    mock_prompt_builder.build_cookie_extraction_prompt.return_value = "Extract cookies from: " + MOCK_ORIGINAL_CONTENT
    mock_llm_provider.generate_content.return_value = "This is not valid JSON."
    mock_response_processor.clean_json_response.return_value = "This is not valid JSON."
    mock_response_processor.parse_json_response.side_effect = ValueError("Invalid JSON") # Simulate parsing error

    result = await cookie_extractor_service.extract_cookie_features(
        original_content=MOCK_ORIGINAL_CONTENT,
        table_content=MOCK_TABLE_CONTENT
    )

    mock_content_analyzer.prepare_content_for_analysis.assert_called_once_with(MOCK_ORIGINAL_CONTENT, MOCK_TABLE_CONTENT)
    mock_prompt_builder.build_cookie_extraction_prompt.assert_called_once()
    mock_llm_provider.generate_content.assert_called_once()
    mock_response_processor.clean_json_response.assert_called_once()
    mock_response_processor.parse_json_response.assert_called_once()
    mock_cookie_feature_repository.insert_many.assert_not_called()

    assert result == PolicyCookieList(is_specific=0, cookies=[])
