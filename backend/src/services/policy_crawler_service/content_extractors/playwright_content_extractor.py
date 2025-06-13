import asyncio
from loguru import logger
from src.services.policy_crawler_service.interfaces.content_extractor_interface import IContentExtractor

class PlaywrightContentExtractor(IContentExtractor):
    """Playwright-based content extraction"""

    def __init__(self, browser_context, timeout: int):
        self.context = browser_context
        self.timeout = timeout

    async def extract_content(self, url: str) -> str:
        page = await self.context.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)
            await asyncio.sleep(2)
            return await page.content()
        except Exception as e:
            logger.error(f"Error extracting content with Playwright: {e}")
            return ""
        finally:
            await page.close()
