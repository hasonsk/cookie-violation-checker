import pytest
from unittest.mock import AsyncMock, MagicMock
from src.services.policy_crawler_service.policy_crawler_service import PolicyCrawlerService
from src.services.policy_crawler_service.crawler_factory import CrawlerFactory
from src.repositories.policy_content_repository import PolicyContentRepository
from src.repositories.policy_storage_repository import PolicyStorageService
from src.services.policy_crawler_service.components.link_discovery import LinkDiscovery
from src.services.policy_crawler_service.components.content_processor import ContentProcessor
from src.services.policy_crawler_service.interfaces.content_extractor_interface import IContentExtractor
from src.services.policy_crawler_service.interfaces.search_provider_interface import ISearchProvider
from src.models.policy import PolicyContent
from src.exceptions.custom_exceptions import PolicyCrawlException

@pytest.fixture
def mock_link_discovery():
    return AsyncMock(spec=LinkDiscovery)

@pytest.fixture
def mock_content_extractor():
    return AsyncMock(spec=IContentExtractor)

@pytest.fixture
def mock_search_provider():
    return AsyncMock(spec=ISearchProvider)

@pytest.fixture
def mock_content_processor():
    return AsyncMock(spec=ContentProcessor)

@pytest.fixture
def mock_policy_storage_service():
    return AsyncMock(spec=PolicyStorageService)

@pytest.fixture
def policy_crawler_service(
    mock_link_discovery,
    mock_content_extractor,
    mock_search_provider,
    mock_content_processor,
    mock_policy_storage_service
):
    return PolicyCrawlerService(
        discovery_service=mock_link_discovery,
        content_extractor=mock_content_extractor,
        search_provider=mock_search_provider,
        content_processor=mock_content_processor,
        storage_repository=mock_policy_storage_service
    )

class TestPolicyCrawlerService:

    @pytest.mark.asyncio
    async def test_extract_policy_existing_policy(self, policy_crawler_service, mock_policy_storage_service):
        # Arrange
        url = "http://example.com/policy"
        mock_policy_storage_service.get_existing_policy.return_value = PolicyContent(
            website_url=url,
            policy_url=url,
            detected_language="en",
            original_content="Existing policy content",
            translated_content=None,
            table_content=[],
            translated_table_content=None,
            error=None
        )

        # Act
        result = await policy_crawler_service.extract_policy(url)

        # Assert
        assert result.original_content == "Existing policy content"
        # PolicyCrawlerService normalizes URL to base URL before checking storage
        from src.utils.url_utils import get_base_url
        mock_policy_storage_service.get_existing_policy.assert_called_once_with(get_base_url(url))

    @pytest.mark.asyncio
    async def test_extract_policy_link_discovery_success(self, policy_crawler_service, mock_link_discovery, mock_content_extractor, mock_content_processor, mock_policy_storage_service):
        # Arrange
        url = "http://example.com"
        policy_url = "http://example.com/privacy"
        mock_link_discovery.discover_policy_link.return_value = policy_url
        mock_content_extractor.extract_content.return_value = "<html><body>Policy content</body></html>"
        mock_content_processor.process_content.return_value = PolicyContent(
            website_url=url,
            policy_url=policy_url,
            detected_language="en",
            original_content="Policy content",
            translated_content=None,
            table_content=[],
            translated_table_content=None,
            error=None
        )
        mock_policy_storage_service.get_existing_policy.return_value = None

        # Act
        result = await policy_crawler_service.extract_policy(url)

        # Assert
        assert result.original_content == "Policy content"
        mock_link_discovery.discover_policy_link.assert_called_once_with(url)
        mock_content_extractor.extract_content.assert_called_once_with(policy_url)
        mock_content_processor.process_content.assert_called_once()
        mock_policy_storage_service.save_policy.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_policy_search_provider_success(self, policy_crawler_service, mock_link_discovery, mock_search_provider, mock_content_extractor, mock_content_processor, mock_policy_storage_service):
        # Arrange
        url = "http://example.com"
        policy_url = "http://example.com/search-privacy"
        mock_link_discovery.discover_policy_link.return_value = None
        mock_search_provider.search_policy.return_value = policy_url
        mock_content_extractor.extract_content.return_value = "<html><body>Search policy content</body></html>"
        mock_content_processor.process_content.return_value = PolicyContent(
            website_url=url,
            policy_url=policy_url,
            detected_language="en",
            original_content="Search policy content",
            translated_content=None,
            table_content=[],
            translated_table_content=None,
            error=None
        )
        mock_policy_storage_service.get_existing_policy.return_value = None

        # Act
        result = await policy_crawler_service.extract_policy(url)

        # Assert
        assert result.original_content == "Search policy content"
        mock_link_discovery.discover_policy_link.assert_called_once_with(url)
        mock_search_provider.search_policy.assert_called_once_with(url)
        mock_content_extractor.extract_content.assert_called_once_with(policy_url)
        mock_content_processor.process_content.assert_called_once()
        mock_policy_storage_service.save_policy.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_policy_no_policy_found(self, policy_crawler_service, mock_link_discovery, mock_search_provider, mock_policy_storage_service):
        # Arrange
        url = "http://example.com"
        mock_link_discovery.discover_policy_link.return_value = None
        mock_search_provider.search_policy.return_value = None
        mock_policy_storage_service.get_existing_policy.return_value = None

        # Act
        result = await policy_crawler_service.extract_policy(url)

        # Assert
        assert result is None
        mock_link_discovery.discover_policy_link.assert_called_once_with(url)
        mock_search_provider.search_policy.assert_called_once_with(url)

    @pytest.mark.asyncio
    async def test_extract_policy_content_extraction_failure(self, policy_crawler_service, mock_link_discovery, mock_content_extractor, mock_policy_storage_service):
        # Arrange
        url = "http://example.com"
        policy_url = "http://example.com/privacy"
        mock_link_discovery.discover_policy_link.return_value = policy_url
        mock_content_extractor.extract_content.side_effect = Exception("Extraction failed")
        mock_policy_storage_service.get_existing_policy.return_value = None

        # Act
        result = await policy_crawler_service.extract_policy(url)

        # Assert
        assert result.error == "Extraction failed"
        assert result.original_content == ""
        mock_link_discovery.discover_policy_link.assert_called_once_with(url)
        mock_content_extractor.extract_content.assert_called_once_with(policy_url)
        mock_policy_storage_service.save_policy.assert_not_called()

    @pytest.mark.asyncio
    async def test_extract_policy_content_processing_failure(self, policy_crawler_service, mock_link_discovery, mock_content_extractor, mock_content_processor, mock_policy_storage_service):
        # Arrange
        url = "http://example.com"
        policy_url = "http://example.com/privacy"
        mock_link_discovery.discover_policy_link.return_value = policy_url
        mock_content_extractor.extract_content.return_value = "<html><body>Policy content</body></html>"
        mock_content_processor.process_content.side_effect = Exception("Processing failed")
        mock_policy_storage_service.get_existing_policy.return_value = None

        # Act
        result = await policy_crawler_service.extract_policy(url)

        # Assert
        assert result.error == "Processing failed"
        assert result.original_content == ""
        mock_link_discovery.discover_policy_link.assert_called_once_with(url)
        mock_content_extractor.extract_content.assert_called_once_with(policy_url)
        mock_content_processor.process_content.assert_called_once()
        mock_policy_storage_service.save_policy.assert_not_called()

    @pytest.mark.asyncio
    async def test_extract_policy_save_policy_failure(self, policy_crawler_service, mock_link_discovery, mock_content_extractor, mock_content_processor, mock_policy_storage_service):
        # Arrange
        url = "http://example.com"
        policy_url = "http://example.com/privacy"
        mock_link_discovery.discover_policy_link.return_value = policy_url
        mock_content_extractor.extract_content.return_value = "<html><body>Policy content</body></html>"
        mock_content_processor.process_content.return_value = PolicyContent(
            website_url=url,
            policy_url=policy_url,
            detected_language="en",
            original_content="Policy content",
            translated_content=None,
            table_content=[],
            translated_table_content=None,
            error=None
        )
        mock_policy_storage_service.get_existing_policy.return_value = None
        mock_policy_storage_service.save_policy.side_effect = Exception("Save failed")

        # Act
        result = await policy_crawler_service.extract_policy(url)

        # Assert
        assert result.error == "Save failed"
        assert result.original_content == "" # Original content is empty on save failure as per implementation
        mock_link_discovery.discover_policy_link.assert_called_once_with(url)
        mock_content_extractor.extract_content.assert_called_once_with(policy_url)
        mock_content_processor.process_content.assert_called_once()
        mock_policy_storage_service.save_policy.assert_called_once()
