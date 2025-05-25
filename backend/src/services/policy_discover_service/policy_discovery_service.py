import logging
import aiohttp
from typing import List, Dict, Any

from schemas.policy_schema import PolicyDiscoveryResult, DiscoveryMethod
from services.policy_discover_service.dom_parser_service import DOMParserService
from services.policy_discover_service.search_service import SearchService
from utils.url_utils import normalize_url, make_absolute_url
from configs.discovery_conf import TIMEOUT, USER_AGENT

logger = logging.getLogger(__name__)

class PolicyDiscoveryService:
    """Main service to find cookie policy URLs through various discovery methods"""

    def __init__(self, timeout: int = None):
        self.timeout = timeout or TIMEOUT
        self.session = None
        self.dom_parser = DOMParserService()
        self.search_service = SearchService()

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={'User-Agent': USER_AGENT}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def find_policy_url(self, website_url: str) -> PolicyDiscoveryResult:
        """Main function to find cookie policy URL using multiple discovery methods"""
        try:
            logger.info(f"Starting policy discovery for: {website_url}")

            # Normalize URL
            website_url = normalize_url(website_url)

            # Try DOM parsing first (most reliable)
            result = await self._find_policy_from_dom(website_url)
            if result.policy_url:
                logger.info(f"Found policy via DOM parsing: {result.policy_url}")
                return result

            # Fallback to Bing search
            bing_url = await self.search_service.search_policy_with_bing(website_url)
            if bing_url:
                result.policy_url = bing_url
                result.discovery_method = DiscoveryMethod.BING_SEARCH
                result.confidence_score = 0.6
                logger.info(f"Found policy via Bing search: {bing_url}")
                return result

            # If no policy found
            result.error = "No cookie policy found"
            logger.warning(f"No cookie policy found for {website_url}")
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
                    best_link = self._rank_policy_links(policy_links, website_url)

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

    def _rank_policy_links(self, links: List[Dict[str, Any]], base_url: str) -> Dict[str, Any]:
        """Rank policy links by relevance and return the best match"""
        if not links:
            return None

        # Process and score links
        scored_links = []
        for link in links:
            url = link['url']

            # Convert relative URLs to absolute
            url = make_absolute_url(url, base_url)

            # Calculate score
            score = link.get('score', 0.5)

            # Boost score for exact matches
            if 'cookie-policy' in url.lower() or 'cookies-policy' in url.lower():
                score += 0.2

            # Boost score for shorter, cleaner URLs
            if len(url.split('/')) <= 4:
                score += 0.1

            scored_links.append({
                'url': url,
                'method': link['method'],
                'score': min(score, 1.0)  # Cap at 1.0
            })

        # Sort by score and return best match
        scored_links.sort(key=lambda x: x['score'], reverse=True)
        return scored_links[0]
