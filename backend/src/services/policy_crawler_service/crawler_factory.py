from concurrent.futures import ThreadPoolExecutor

from src.repositories.policy_content_repository import PolicyContentRepository
# from src.services.policy_crawler_service.content_extractors import scrapy_content_extractor # Updated path
from src.services.policy_crawler_service.content_extractors.playwright_content_extractor import PlaywrightContentExtractor
from src.services.policy_crawler_service.components.content_processor import ContentProcessor
from src.services.policy_crawler_service.components.link_discovery import LinkDiscovery
from src.repositories.policy_storage_repository import PolicyStorageService
from src.services.policy_crawler_service.interfaces.content_extractor_interface import IContentExtractor
from src.services.policy_crawler_service.interfaces.search_provider_interface import ISearchProvider
from src.services.policy_crawler_service.policy_crawler_service import PolicyCrawlerService
from src.services.policy_crawler_service.search_providers.bing_search import BingSearch
from src.utils.cache_utils import CacheManager
from src.utils.dom_parser_utils import DOMParserService
from src.utils.table_extractor import TableExtractor
from src.utils.text_processing import TextProcessor
from src.utils.translation_utils import TranslationManager


class CrawlerFactory:
    """Factory for creating policy crawler with different configurations"""

    @staticmethod
    def create_playwright_bing_extractor(
        policy_content_repo: PolicyContentRepository,
        browser_context,
        timeout: int = 30
    ) -> PolicyCrawlerService:
        """Create extractor using Playwright + Bing"""

        content_extractor = PlaywrightContentExtractor(browser_context, timeout)
        search_provider = BingSearch(browser_context)

        return CrawlerFactory._create_extractor(
            policy_content_repo, content_extractor, search_provider
        )

    @staticmethod
    def _create_extractor(
        policy_content_repo: PolicyContentRepository,
        content_extractor: IContentExtractor,
        search_provider: ISearchProvider
    ) -> PolicyCrawlerService:
        """Internal method to create extractor with given components"""

        executor = ThreadPoolExecutor(max_workers=4)

        dom_parser = DOMParserService()
        text_processor = TextProcessor(executor)
        translation_manager = TranslationManager(executor)
        table_extractor = TableExtractor()
        cache_manager = CacheManager()

        # Create specialized components
        discovery_service = LinkDiscovery(dom_parser, content_extractor)
        content_processor = ContentProcessor(text_processor, translation_manager, table_extractor)
        storage_repository = PolicyStorageService(policy_content_repo, cache_manager)

        return PolicyCrawlerService(
            discovery_service=discovery_service,
            content_extractor=content_extractor,
            search_provider=search_provider,
            content_processor=content_processor,
            storage_repository=storage_repository
        )
