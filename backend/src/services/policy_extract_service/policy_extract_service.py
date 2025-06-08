import asyncio
import json
from loguru import logger
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
from playwright.async_api import async_playwright, Browser, BrowserContext

from src.configs.crawler_config import (
    USER_AGENT, CRAWLER_TIMEOUT, BROWSER_CONFIG,
    BROWSER_CONTEXT_CONFIG, THREAD_POOL_MAX_WORKERS
)
from src.schemas.policy_schema import PolicyContent
from src.utils.text_processing import TextProcessor
from src.utils.translation_utils import TranslationManager
from src.utils.table_extractor import TableExtractor
from src.utils.cache_utils import CacheManager
from src.repositories.policy_content_repository import PolicyContentRepository

class PolicyExtractService:
    def __init__(self, policy_repository: PolicyContentRepository):
        self.user_agent = USER_AGENT
        self.timeout = CRAWLER_TIMEOUT

        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._executor = ThreadPoolExecutor(max_workers=THREAD_POOL_MAX_WORKERS)

        # Initialize utility classes
        self.text_processor = TextProcessor(self._executor)
        self.translation_manager = TranslationManager(self._executor)
        self.table_extractor = TableExtractor()
        self.cache_manager = CacheManager()
        self.policy_repository = policy_repository

    async def __aenter__(self):
        """Async context manager entry"""
        await self._initialize_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._cleanup_browser()

    async def _initialize_browser(self):
        """Initialize browser context for reuse"""
        if not self._browser:
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch(**BROWSER_CONFIG)
            self._context = await self._browser.new_context(
                user_agent=self.user_agent,
                **BROWSER_CONTEXT_CONFIG
            )

    async def _cleanup_browser(self):
        """Cleanup browser resources"""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()

    async def extract_policy_content(
        self,
        website_url: str,
        policy_url: Optional[str] = None,
        translate_to_english: bool = True,
        force_refresh: bool = False
    ) -> PolicyContent:
        """Main method to extract policy content from a website"""
        try:
            # Check cache first
            if not force_refresh:
                cached_result = await self.cache_manager.get_cached_content(website_url)
                if cached_result:
                    logger.info(f"Cache hit for URL: {website_url}")
                    return cached_result
            logger.info("START to extract policy content")
            # Initialize browser if not already done
            if not self._browser:
                await self._initialize_browser()

            if not policy_url:
                return PolicyContent(
                    website_url=website_url,
                    policy_url=None,
                    original_content="",
                    translated_content=None,
                    detected_language=None,
                    table_content=[],
                    translated_table_content=None,
                    error="Cookie policy URL not found"
                )

            page_content = await self._extract_page_content(policy_url)

            # Process extracted content
            policy_content = await self._process_content(
                website_url=website_url,
                policy_url=policy_url,
                html_content=page_content,
                translate_to_english=translate_to_english
            )

            # Cache the result
            # await self.cache_manager.cache_content(website_url, policy_content)

            # Save to database
            await self.policy_repository.create_policy_content(policy_content.dict())
            logger.info(f"Policy content for {website_url} saved to database.")

            return policy_content

        except Exception as e:
            logger.error(f"Error extracting policy content from {website_url}: {e}")
            # Even if an error occurs, attempt to save the error state to the database
            error_policy_content = PolicyContent(
                website_url=website_url,
                policy_url=policy_url,
                original_content="",
                translated_content=None,
                detected_language=None,
                table_content=[],
                translated_table_content=None,
                error=str(e)
            )
            await self.policy_repository.create_policy_content(error_policy_content)
            return error_policy_content

    async def _extract_page_content(self, policy_url: str) -> str:
        """Extract HTML content from policy page with retry logic"""
        page = await self._context.new_page()

        try:
            try:
                await page.goto(policy_url, wait_until="networkidle", timeout=self.timeout * 1000)
            except:
                logger.warning(f"Networkidle timeout for {policy_url}, trying domcontentloaded")
                await page.goto(policy_url, wait_until="domcontentloaded", timeout=self.timeout * 1000)

            await asyncio.sleep(2)
            return await page.content()

        except Exception as e:
            logger.error(f"Error extracting page content from {policy_url}: {e}")
            return ""
        finally:
            await page.close()

    async def _process_content(
        self,
        website_url: str,
        policy_url: str,
        html_content: str,
        translate_to_english: bool = True
    ) -> PolicyContent:
        """Process extracted HTML content into structured data"""

        # Extract text content
        policy_text = await self.text_processor.extract_clean_text(html_content)

        # Detect language
        detected_language = await self.text_processor.detect_language_async(policy_text)

        # Extract tables
        table_data = self.table_extractor.extract_tables_from_html(html_content)

        # Handle translation
        translated_text = None
        translated_table_content = None

        if translate_to_english and detected_language and detected_language != 'en':
            translated_text = await self.translation_manager.translate_content_to_english(policy_text)

            if table_data:
                table_json = json.dumps([table for table in table_data], ensure_ascii=False, indent=2)
                translated_table_content = await self.translation_manager.translate_content_to_english(table_json)

        response =  PolicyContent(
            website_url=website_url,
            policy_url=policy_url,
            original_content=policy_text,
            translated_content=translated_text,
            detected_language=detected_language,
            table_content=table_data,
            translated_table_content=translated_table_content
        )

        return response
