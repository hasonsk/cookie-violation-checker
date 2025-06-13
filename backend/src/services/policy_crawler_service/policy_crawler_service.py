import asyncio
import json
from loguru import logger
import aiohttp
from playwright.async_api import async_playwright, Browser, BrowserContext
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

from src.utils.url_utils import normalize_url, get_base_url
from src.schemas.policy import PolicyDiscoveryResult, PolicyContent, DiscoveryMethod
from src.utils.dom_parser_utils import DOMParserService
from src.utils.search_utils import SearchService
from src.repositories.policy_content_repository import PolicyContentRepository
from src.utils.retry_utils import retry
from src.configs.settings import settings
from src.utils.text_processing import TextProcessor
from src.utils.translation_utils import TranslationManager
from src.utils.table_extractor import TableExtractor
from src.utils.cache_utils import CacheManager


class PolicyCrawlerService:
    def __init__(self,
                 policy_content_repo: PolicyContentRepository,
                 timeout: int = settings.crawler.CRAWLER_TIMEOUT,
                 use_playwright: bool = True):
        self.timeout = timeout
        self.session = None
        self.use_playwright = use_playwright
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self.playwright = None
        self._executor = ThreadPoolExecutor(max_workers=settings.crawler.THREAD_POOL_MAX_WORKERS)

        self.policy_content_repo = policy_content_repo

        self.dom_parser = DOMParserService()
        self.search_service = None  # Will be initialized when browser is available

        # Initialize utility classes for content extraction
        self.text_processor = TextProcessor(self._executor)
        self.translation_manager = TranslationManager(self._executor)
        self.table_extractor = TableExtractor()
        self.cache_manager = CacheManager()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={
                'User-Agent': settings.crawler.USER_AGENT
            }
        )

        if self.use_playwright:
            self.playwright = await async_playwright().start()
            self._browser = await self.playwright.chromium.launch(
                headless=settings.crawler.BROWSER_HEADLESS,
                args=settings.crawler.BROWSER_ARGS
            )
            self._context = await self._browser.new_context(
                user_agent=settings.crawler.USER_AGENT,
                viewport={
                    "width": settings.crawler.BROWSER_VIEWPORT_WIDTH,
                    "height": settings.crawler.BROWSER_VIEWPORT_HEIGHT,
                },
                device_scale_factor=settings.crawler.BROWSER_DEVICE_SCALE_FACTOR,
                extra_http_headers=settings.crawler.BROWSER_EXTRA_HTTP_HEADERS,
            )
            self.search_service = SearchService(self._browser)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()

        if self.playwright:
            await self.playwright.stop()

    async def find_and_extract_policy(self, web_url: str, force_refresh: bool = False) -> Optional[PolicyContent]:
        """
        Finds and extracts cookie policy content for a given URL.
        Follows the sequence diagram: DB check -> DOM parsing -> Bing search.
        """
        web_url = normalize_url(web_url)
        root_url = get_base_url(web_url)

        # 1. Check if policy already exists in DB
        if not force_refresh:
            existing_policy = await self.policy_content_repo.get_by_website_url(root_url)
            logger.warning(f"Checking database for existing policy for {existing_policy}...")
            if existing_policy:
                logger.info(f"Policy for {web_url} found in DB. Returning existing policy object.")
                return existing_policy

        logger.info(f"Policy for {web_url} not found in DB or force refresh. Starting crawl process.")

        policy_url = None
        main_page_html = None

        # 2. Fetch main page HTML
        try:
            async with self.session.get(root_url) as response:
                if response.status == 200:
                    main_page_html = await response.text()
                else:
                    logger.warning(f"Failed to fetch main page {root_url}: HTTP {response.status}")
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching main page {root_url}: {e}")
            return None

        # 3. Find policy link on main page
        if main_page_html:
            policy_links = self.dom_parser.parse_policy_links_from_dom(main_page_html)
            if policy_links:
                best_link = self.dom_parser.rank_policy_links(policy_links, root_url)
                policy_url = best_link['url']
                logger.info(f"Found policy link on main page: {policy_url}")

        # 4. Fallback to Bing search if no link found on main page
        if not policy_url and self.search_service:
            logger.info(f"No policy link found on main page. Falling back to Bing search for {root_url}.")
            policy_url = await self.search_service.search_policy_with_bing(root_url)
            if policy_url:
                logger.info(f"Found policy via Bing search: {policy_url}")
            else:
                logger.warning(f"No policy found via Bing search for {root_url}.")
                return None

        if not policy_url:
            logger.warning(f"Could not find any policy URL for {web_url}.")
            return None

        # 5. Extract and process content from the discovered policy URL
        try:
            policy_content_obj = await self._extract_and_process_policy_content(
                website_url=web_url,
                policy_url=policy_url,
                translate_to_english=True, # Assuming always translate for now
            )
            if policy_content_obj and policy_content_obj.original_content:
                # Cache the result
                await self.cache_manager.cache_content(web_url, policy_content_obj)
                # Save to database
                await self.policy_content_repo.create_policy_content(policy_content_obj.dict(by_alias=True))
                logger.info(f"Policy content for {web_url} saved to database.")
                return policy_content_obj
            else:
                logger.error(f"Failed to extract content from policy URL: {policy_url}")
                return None
        except Exception as e:
            logger.error(f"Error during content extraction for {policy_url}: {e}")
            return None

    async def _extract_and_process_policy_content(
        self,
        website_url: str,
        policy_url: str,
        translate_to_english: bool = True
    ) -> PolicyContent:
        """
        Extracts and processes policy content from a given policy URL.
        This method does not handle DB lookup or saving, only content extraction and processing.
        """
        try:
            page_content = await self._extract_page_content(policy_url)

            if not page_content:
                raise ValueError(f"No content extracted from {policy_url}")

            policy_content = await self._process_content(
                website_url=website_url,
                policy_url=policy_url,
                html_content=page_content,
                translate_to_english=translate_to_english
            )
            return policy_content

        except Exception as e:
            logger.error(f"Error extracting and processing policy content from {policy_url}: {e}")
            return PolicyContent(
                website_url=website_url,
                policy_url=policy_url,
                original_content="",
                translated_content=None,
                detected_language=None,
                table_content=[],
                translated_table_content=None,
                error=str(e)
            )

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
