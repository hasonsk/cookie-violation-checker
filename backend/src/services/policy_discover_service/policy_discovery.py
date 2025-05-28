import re
import json
import logging
import asyncio
import aiohttp
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from dataclasses import dataclass
from enum import Enum
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiscoveryMethod(Enum):
    LINK_TAG = "link_tag"
    FOOTER_LINK = "footer_link"
    NAVIGATION_LINK = "navigation_link"
    BING_SEARCH = "bing_search"
    SITEMAP = "sitemap"

class PolicyDiscoveryResult(BaseModel):
    website_url: str
    policy_url: Optional[str] = None
    discovery_method: Optional[DiscoveryMethod] = None
    error: Optional[str] = None
    confidence_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "website_url": self.website_url,
            "policy_url": self.policy_url,
            "discovery_method": self.discovery_method.value if self.discovery_method else None,
            "error": self.error,
            "confidence_score": self.confidence_score
        }

class PolicyFinderService:
    """Service to find cookie policy URLs through various discovery methods"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = None

        # Enhanced patterns for cookie policy detection
        self.cookie_policy_patterns = [
            # English patterns
            r'cookie[s]?\s*policy',
            r'cookie[s]?\s*notice',
            r'cookie[s]?\s*statement',
            r'cookie[s]?\s*information',
            r'cookie[s]?\s*settings',
            r'use\s*of\s*cookie[s]?',

            # Vietnamese patterns
            r'chính\s*sách\s*cookie[s]?',
            r'thông\s*báo\s*cookie[s]?',
            r'sử\s*dụng\s*cookie[s]?',
            r'quy\s*định\s*cookie[s]?',

            # Other languages
            r'política\s*de\s*cookie[s]?',  # Spanish/Portuguese
            r'politique\s*de\s*cookie[s]?',  # French
            r'cookie[s]?\s*richtlinie',  # German
            r'informativa\s*cookie[s]?',  # Italian
        ]

        # Common URL patterns
        self.url_patterns = [
            r'/cookie[s]?[-_]?policy',
            r'/cookie[s]?[-_]?notice',
            r'/privacy.*cookie',
            r'/legal.*cookie',
            r'/cookie[s]?$',
        ]

        # Selectors for finding policy links
        self.policy_selectors = [
            # Footer selectors
            'footer a[href*="cookie"]',
            'footer a[href*="privacy"]',
            '.footer a[href*="cookie"]',
            '.site-footer a[href*="cookie"]',

            # Navigation selectors
            'nav a[href*="cookie"]',
            '.navigation a[href*="cookie"]',
            '.nav a[href*="cookie"]',

            # Generic link selectors
            'a[href*="cookie-policy"]',
            'a[href*="cookies-policy"]',
            'a[href*="cookie_policy"]',
            'a[href*="cookies_policy"]',

            # Link tag selectors
            'link[rel*="policy"]',
            'link[href*="cookie"]',
        ]

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def find_policy_url(self, website_url: str) -> PolicyDiscoveryResult:
        """
        Main function to find cookie policy URL using multiple discovery methods

        Args:
            website_url: The website URL to search for cookie policy

        Returns:
            PolicyDiscoveryResult with discovered policy URL or error
        """
        try:
            logger.info(f"Starting policy discovery for: {website_url}")

            # Normalize URL
            website_url = self._normalize_url(website_url)

            # Try DOM parsing first (most reliable)
            result = await self._find_policy_from_dom(website_url)
            if result.policy_url:
                logger.info(f"Found policy via DOM parsing: {result.policy_url}")
                return result

            print("SEARCH WITH BING -----------")
            # Fallback to Bing search (mocked for now)
            bing_url = await self.search_policy_with_bing(website_url)
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
                policy_links = self.parse_policy_links_from_dom(html_content)

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

    def parse_policy_links_from_dom(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Parse HTML content to find cookie policy links

        Args:
            html_content: HTML content to parse

        Returns:
            List of potential policy links with metadata
        """
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            found_links = []

            # Method 1: Check for link tags
            link_tags = soup.find_all('link', href=True)
            for link in link_tags:
                href = link.get('href', '')
                rel = link.get('rel', [])

                if self._is_policy_link(href) or 'policy' in str(rel).lower():
                    found_links.append({
                        'url': href,
                        'method': DiscoveryMethod.LINK_TAG,
                        'text': link.get('title', ''),
                        'score': 0.9
                    })

            # Method 2: Check footer links
            footer_links = self._find_links_in_section(soup, ['footer', '.footer', '.site-footer'])
            found_links.extend([{**link, 'method': DiscoveryMethod.FOOTER_LINK, 'score': 0.8}
                               for link in footer_links])

            # Method 3: Check navigation links
            nav_links = self._find_links_in_section(soup, ['nav', '.navigation', '.nav', '.menu'])
            found_links.extend([{**link, 'method': DiscoveryMethod.NAVIGATION_LINK, 'score': 0.7}
                               for link in nav_links])

            # Method 4: Check all links with policy patterns
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)

                if self._is_policy_link(href) or self._is_policy_text(text):
                    # Avoid duplicates
                    if not any(existing['url'] == href for existing in found_links):
                        found_links.append({
                            'url': href,
                            'method': DiscoveryMethod.FOOTER_LINK,  # Default method
                            'text': text,
                            'score': 0.6
                        })

            logger.info(f"Found {len(found_links)} potential policy links")
            return found_links

        except Exception as e:
            logger.error(f"Error parsing DOM: {str(e)}")
            return []

    def _find_links_in_section(self, soup: BeautifulSoup, selectors: List[str]) -> List[Dict[str, Any]]:
        """Find policy links in specific page sections"""
        links = []

        for selector in selectors:
            sections = soup.select(selector)
            for section in sections:
                section_links = section.find_all('a', href=True)
                for link in section_links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)

                    if self._is_policy_link(href) or self._is_policy_text(text):
                        links.append({
                            'url': href,
                            'text': text
                        })

        return links

    def _is_policy_link(self, url: str) -> bool:
        """Check if URL matches cookie policy patterns"""
        url_lower = url.lower()
        return any(re.search(pattern, url_lower, re.IGNORECASE) for pattern in self.url_patterns)

    def _is_policy_text(self, text: str) -> bool:
        """Check if link text matches cookie policy patterns"""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in self.cookie_policy_patterns)

    def _rank_policy_links(self, links: List[Dict[str, Any]], base_url: str) -> Dict[str, Any]:
        """Rank policy links by relevance and return the best match"""
        if not links:
            return None

        # Process and score links
        scored_links = []
        for link in links:
            url = link['url']

            # Convert relative URLs to absolute
            if not url.startswith(('http://', 'https://')):
                url = urljoin(base_url, url)

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

    async def search_policy_with_bing(self, website_url: str) -> Optional[str]:
        """
        Search for cookie policy using Bing API (mocked for now)

        Args:
            website_url: Website URL to search policy for

        Returns:
            Optional policy URL if found
        """
        try:
            # Mock implementation - in production, this would use actual Bing Search API
            logger.info(f"Searching policy with Bing for: {website_url}")

            # Simulated search query
            domain = urlparse(website_url).netloc
            search_queries = [
                f'site:{domain} "cookie policy"',
                f'site:{domain} "privacy policy" cookies',
                f'site:{domain} "use of cookies"'
            ]

            # Mock response - in production, implement actual API call
            await asyncio.sleep(0.1)  # Simulate API delay

            # Return mock result for demonstration
            if 'example.com' in website_url:
                return f"{website_url.rstrip('/')}/cookie-policy"

            logger.info("Bing search completed - no results found")
            return None

        except Exception as e:
            logger.error(f"Bing search error: {str(e)}")
            return None

    def _normalize_url(self, url: str) -> str:
        """Normalize URL format"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url.rstrip('/')

# Usage example and testing
async def main():
    """Example usage of the PolicyFinderService"""
    test_urls = [
        "https://stackoverflow.com",
        "https://www.vivaisquadrito.it/",
        "https://google.com",
        "https://daotao.ai"
    ]

    async with PolicyFinderService() as finder:
        for url in test_urls:
            result = await finder.find_policy_url(url)
            print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
            print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
