from typing import Optional
from loguru import logger
from src.services.policy_crawler_service.interfaces.content_extractor_interface import IContentExtractor
from src.utils.dom_parser_utils import DOMParserService


class LinkDiscovery:
    """Responsible only for discovering policy links from main pages"""

    def __init__(self, dom_parser: DOMParserService, content_extractor: IContentExtractor):
        self.dom_parser = dom_parser
        self.content_extractor = content_extractor

    async def discover_policy_link(self, root_url: str) -> Optional[str]:
        """Discover policy link from main page DOM"""
        try:
            html_content = await self.content_extractor.extract_content(root_url)
            if not html_content:
                return None

            policy_links = self.dom_parser.parse_policy_links_from_dom(html_content)
            if policy_links:
                best_link = self.dom_parser.rank_policy_links(policy_links, root_url)
                return best_link['url']

            return None
        except Exception as e:
            logger.error(f"Error discovering policy link: {e}")
            return None
