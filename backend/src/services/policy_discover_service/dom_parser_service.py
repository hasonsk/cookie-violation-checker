import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup

from schemas.policy_schema import DiscoveryMethod
from utils.pattern_matcher import PatternMatcher
from configs.discovery_conf import TIMEOUT, USER_AGENT, COOKIE_POLICY_PATTERNS, URL_PATTERNS, POLICY_SELECTORS, FOOTER_SELECTORS, NAV_SELECTORS

logger = logging.getLogger(__name__)

class DOMParserService:
    """Service for parsing HTML DOM to find policy links"""

    def __init__(self):
        self.pattern_matcher = PatternMatcher()

    def parse_policy_links_from_dom(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse HTML content to find cookie policy links"""
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
            footer_links = self._find_links_in_section(soup, FOOTER_SELECTORS)
            found_links.extend([{**link, 'method': DiscoveryMethod.FOOTER_LINK, 'score': 0.8}
                               for link in footer_links])

            # Method 3: Check navigation links
            nav_links = self._find_links_in_section(soup, NAV_SELECTORS)
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
                            'method': DiscoveryMethod.FOOTER_LINK,
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
        return self.pattern_matcher.is_policy_link(url, URL_PATTERNS)

    def _is_policy_text(self, text: str) -> bool:
        """Check if link text matches cookie policy patterns"""
        return self.pattern_matcher.is_policy_text(text, COOKIE_POLICY_PATTERNS)
