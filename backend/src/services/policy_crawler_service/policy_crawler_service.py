import asyncio
import json
from loguru import logger
from typing import Optional

from src.schemas.policy import PolicyContent
from src.utils.url_utils import normalize_url, get_base_url
from src.repositories.policy_content_repository import PolicyContentRepository
from src.repositories.policy_storage_repository import PolicyStorageService
from src.services.policy_crawler_service.interfaces.content_extractor_interface import IContentExtractor
from src.services.policy_crawler_service.interfaces.search_provider_interface import ISearchProvider
from src.services.policy_crawler_service.components.link_discovery import LinkDiscovery
from src.services.policy_crawler_service.components.content_processor import ContentProcessor


class PolicyCrawlerService:
    """
    Orchestrates the policy extraction process, utilizing various components
    for link discovery, content extraction, content processing, and storage.
    """

    def __init__(self,
                 discovery_service: LinkDiscovery,
                 content_extractor: IContentExtractor,
                 search_provider: ISearchProvider,
                 content_processor: ContentProcessor,
                 storage_repository: PolicyStorageService):
        self.discovery_service = discovery_service
        self.content_extractor = content_extractor
        self.search_provider = search_provider
        self.content_processor = content_processor
        self.storage_repository = storage_repository

    async def extract_policy(self, web_url: str, force_refresh: bool = False) -> Optional[PolicyContent]:
        """
        Finds and extracts cookie policy content for a given URL.
        Follows the sequence diagram: DB check -> DOM parsing -> Search.
        """
        web_url = normalize_url(web_url)
        root_url = get_base_url(web_url)

        # 1. Check if policy already exists in DB
        if not force_refresh:
            existing_policy = await self.storage_repository.get_existing_policy(root_url)
            if existing_policy:
                logger.info(f"Policy for {web_url} found in DB. Returning existing policy object.")
                return existing_policy

        logger.info(f"Policy for {web_url} not found in DB or force refresh. Starting extraction process.")

        policy_url = None

        # 2. Find policy link on main page
        policy_url = await self.discovery_service.discover_policy_link(root_url)
        if policy_url:
            logger.info(f"Found policy link on main page: {policy_url}")
        else:
            # 3. Fallback to search if no link found on main page
            logger.info(f"No policy link found on main page. Falling back to search for {root_url}.")
            policy_url = await self.search_provider.search_policy(root_url)
            if policy_url:
                logger.info(f"Found policy via search: {policy_url}")
            else:
                logger.warning(f"No policy found via search for {root_url}.")
                return None

        if not policy_url:
            logger.warning(f"Could not find any policy URL for {web_url}.")
            return None

        # 4. Extract and process content from the discovered policy URL
        try:
            html_content = await self.content_extractor.extract_content(policy_url)
            if not html_content:
                raise ValueError(f"No content extracted from {policy_url}")

            policy_content_obj = await self.content_processor.process_content(
                website_url=root_url,
                policy_url=policy_url,
                html_content=html_content,
                translate_to_english=True,
            )

            if policy_content_obj and policy_content_obj.original_content:
                await self.storage_repository.save_policy(root_url, policy_content_obj)
                logger.info(f"Policy content for {web_url} saved to database.")
                return policy_content_obj
            else:
                logger.error(f"Failed to extract or process content from policy URL: {policy_url}")
                return None
        except Exception as e:
            logger.error(f"Error during content extraction for {policy_url}: {e}")
            return PolicyContent(
                website_url=root_url,
                policy_url=policy_url,
                original_content="",
                translated_content=None,
                detected_language=None,
                table_content=[],
                translated_table_content=None,
                error=str(e)
            )
