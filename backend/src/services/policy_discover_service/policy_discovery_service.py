from loguru import logger
import aiohttp
from urllib.parse import urlparse
from playwright.async_api import async_playwright

from .policy_discovery import PolicyDiscoveryResult, DiscoveryMethod
from .dom_parser_service import DOMParserService
from .search_service import SearchService

# logger = logging.getLogger(__name__)


class PolicyDiscoveryService:
    def __init__(self, timeout: int = 30, use_playwright: bool = True):
        self.timeout = timeout
        self.session = None
        self.use_playwright = use_playwright
        self.browser = None
        self.playwright = None

        self.dom_parser = DOMParserService()
        self.search_service = None  # Will be initialized when browser is available

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )

        if self.use_playwright:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            self.search_service = SearchService(self.browser)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

        if self.browser:
            await self.browser.close()

        if self.playwright:
            await self.playwright.stop()

    async def find_policy_url(self, website_url: str) -> PolicyDiscoveryResult:
        try:
            # Normalize URL
            website_url = self._normalize_url(website_url)
            root_url = self._get_base_url(website_url)

            # Try DOM parsing first (most reliable)
            result = await self._find_policy_from_dom(root_url)
            if result.policy_url:
                logger.info(f"Found policy via DOM parsing: {result.policy_url}")
                return result

            # Fallback to Bing search
            if self.search_service:
                bing_url = await self.search_service.search_policy_with_bing(root_url)
                logger.info(bing_url)
                if bing_url:
                    result.policy_url = bing_url
                    result.discovery_method = DiscoveryMethod.BING_SEARCH
                    result.confidence_score = 0.6
                    logger.info(f"Found policy via Bing search: {bing_url}")
                    return result

            # If no policy found
            result.error = "No cookie policy found"
            logger.warning(f"No cookie policy found for {root_url}")
            return result

        except Exception as e:
            logger.error(f"Error finding policy for {website_url}: {str(e)}")
            return PolicyDiscoveryResult(
                website_url=website_url,
                error=str(e)
            )

    async def _find_policy_from_dom(self, website_url: str) -> PolicyDiscoveryResult:
        """Find policy URL by parsing the website's DOM"""
        try:
            async with self.session.get(website_url) as response:
                if response.status != 200:
                    return PolicyDiscoveryResult(
                        website_url=website_url,
                        error=f"HTTP {response.status}"
                    )

                html_content = await response.text()
                policy_links = self.dom_parser.parse_policy_links_from_dom(html_content)

                if policy_links:
                    # Get the best match
                    best_link = self.dom_parser.rank_policy_links(policy_links, website_url)

                    return PolicyDiscoveryResult(
                        website_url=website_url,
                        policy_url=best_link['url'],
                        discovery_method=best_link['method'],
                        confidence_score=best_link['score']
                    )

                return PolicyDiscoveryResult(website_url=website_url)

        except Exception as e:
            logger.error(f"DOM parsing error for {website_url}: {str(e)}")
            return PolicyDiscoveryResult(
                website_url=website_url,
                error=f"DOM parsing failed: {str(e)}"
            )

    def _normalize_url(self, url: str) -> str:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url.rstrip('/')

    def _get_base_url(self, full_url: str) -> str:
        _url = urlparse(full_url)
        return f"{_url.scheme}://{_url.netloc}"
