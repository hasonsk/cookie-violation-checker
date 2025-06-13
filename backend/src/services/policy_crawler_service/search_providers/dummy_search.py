from typing import Optional
from src.services.policy_crawler_service.interfaces.search_provider_interface import ISearchProvider
from loguru import logger

class DummySearch(ISearchProvider):
    """A dummy search provider that always returns None."""

    async def search_policy(self, domain: str) -> Optional[str]:
        logger.info(f"DummySearch: No policy found for {domain} (always returns None).")
        return None
