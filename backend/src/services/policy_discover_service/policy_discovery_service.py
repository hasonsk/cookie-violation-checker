from loguru import logger
import aiohttp
from playwright.async_api import async_playwright
from utils.url_utils import normalize_url, get_base_url
from schemas.policy_schema import PolicyDiscoveryResult, DiscoveryMethod
from configs.crawler_config import USER_AGENT
from .dom_parser_service import DOMParserService
from .search_service import SearchService
from repositories.discovery_repo import PolicyDiscoveryRepository

class PolicyDiscoveryService:
    def __init__(self, timeout: int = 30, use_playwright: bool = True, discovery_repo = PolicyDiscoveryRepository):
        self.timeout = timeout
        self.session = None
        self.use_playwright = use_playwright
        self.browser = None
        self.playwright = None
        self.discovery_repo = discovery_repo

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
        logger.info(f"I have our {self.session}, {self.browser}, {self.playwright}")
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
            website_url = normalize_url(website_url)
            root_url = get_base_url(website_url)

            # Try DOM parsing first (most reliable)
            result = await self._find_policy_from_dom(root_url)
            if result.policy_url:
                logger.info(f"Found policy via DOM parsing: {result.policy_url}")
            else:
                # Fallback to Bing search if DOM parsing fails
                result = await self._fallback_to_bing_search(result, root_url)

            # Save the result to the repository
            await self._save_discovery_result(website_url, result)
            return result

        except Exception as e:
            logger.error(f"Error finding policy for {website_url}: {str(e)}")
            error_result = PolicyDiscoveryResult(website_url=website_url, error=str(e))
            await self._save_discovery_result(website_url, error_result)
            return error_result

    async def _fallback_to_bing_search(self, result: PolicyDiscoveryResult, root_url: str) -> PolicyDiscoveryResult:
        if self.search_service:
            bing_url = await self.search_service.search_policy_with_bing(root_url)
            if bing_url:
                logger.info(f"Found policy via Bing search: {bing_url}")
                result.policy_url = bing_url
                result.discovery_method = DiscoveryMethod.BING_SEARCH
                result.confidence_score = 0.6
            else:
                logger.warning(f"No cookie policy found for {root_url}")
                result.error = "No cookie policy found"
        return result

    async def _save_discovery_result(self, website_url: str, result: PolicyDiscoveryResult):
        await self.discovery_repo.insert_one({
            "website_url": website_url,
            "policy_url": result.policy_url,
            "discovery_method": result.discovery_method.value if result.discovery_method else None,
            "confidence_score": result.confidence_score,
            "error": result.error,
        })

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
