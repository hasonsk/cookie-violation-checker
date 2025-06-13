import re
from loguru import logger
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from src.schemas.policy import DiscoveryMethod
from src.configs.settings import settings

class DOMParserService:
    def __init__(self):
        self.cookie_policy_patterns = settings.policy_discovery.COOKIE_POLICY_PATTERNS
        self.url_patterns = settings.policy_discovery.URL_PATTERNS
        self.FOOTER_SELECTORS = settings.policy_discovery.FOOTER_SELECTORS
        self.NAV_SELECTORS = settings.policy_discovery.NAV_SELECTORS

    def parse_policy_links_from_dom(self, html_content: str) -> List[Dict[str, Any]]:
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            found_links = []

            # Method 1: Check for link tags
            link_tags = soup.find_all('link', href=True)
            for link in link_tags:
                href = link.get('href', '')
                rel = link.get('rel', [])

                if self._is_cookie_policy_link(href) or 'cookie' in str(rel).lower():
                    found_links.append({
                        'url': href,
                        'method': DiscoveryMethod.LINK_TAG,
                        'text': link.get('title', ''),
                        'score': 0.9
                    })

            # Method 2: Check footer links
            footer_links = self._find_links_in_section(soup, self.FOOTER_SELECTORS)
            found_links.extend([{**link, 'method': DiscoveryMethod.FOOTER_LINK, 'score': 0.8}
                               for link in footer_links])

            # Method 3: Check navigation links
            nav_links = self._find_links_in_section(soup, self.NAV_SELECTORS)
            found_links.extend([{**link, 'method': DiscoveryMethod.NAVIGATION_LINK, 'score': 0.7}
                               for link in nav_links])

            # Method 4: Check all links with policy patterns
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)

                if self._is_cookie_policy_link(href) or self._is_policy_text(text):
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

                    if self._is_cookie_policy_link(href) or self._is_policy_text(text):
                        links.append({
                            'url': href,
                            'text': text
                        })

        return links

    def _is_cookie_policy_link(self, url: str) -> bool:
        """Check if URL matches cookie policy patterns"""
        url_lower = url.lower()
        return any(re.search(pattern, url_lower, re.IGNORECASE) for pattern in self.url_patterns)

    def _is_policy_text(self, text: str) -> bool:
        """Check if link text matches cookie policy patterns"""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in self.cookie_policy_patterns)

    def rank_policy_links(self, links: List[Dict[str, Any]], base_url: str) -> Dict[str, Any]:
        """Rank policy links by relevance and return the best match"""
        if not links:
            return None

        # Process and score links
        scored_links = []
        for link in links:
            url = link['url']

            if not url.startswith(('http://', 'https://')):
                url = urljoin(base_url, url)

            score = link.get('score', 0.5)

            if 'cookie-policy' in url.lower() or 'cookies-policy' in url.lower():
                score += 0.2

            if len(url.split('/')) <= 4:
                score += 0.1

            scored_links.append({
                'url': url,
                'method': link['method'],
                'score': min(score, 1.0)
            })

        scored_links.sort(key=lambda x: x['score'], reverse=True)
        return scored_links[0]
