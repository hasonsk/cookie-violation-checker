from typing import Optional
from src.utils.search_utils import SearchService
from src.services.policy_crawler_service.interfaces.search_provider_interface import ISearchProvider


class BingSearch(ISearchProvider):
    """Bing search implementation"""

    def __init__(self, browser):
        self.browser = browser
        self.search_service = SearchService(browser)

    async def search_policy(self, domain: str) -> Optional[str]:
        return await self.search_service.search_policy_with_bing(domain)
