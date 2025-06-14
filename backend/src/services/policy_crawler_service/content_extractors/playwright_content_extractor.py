import asyncio
from loguru import logger
from src.services.policy_crawler_service.interfaces.content_extractor_interface import IContentExtractor

class PlaywrightContentExtractor(IContentExtractor):
    """Playwright-based content extraction"""

    def __init__(self, browser_context, timeout: int):
        self.context = browser_context
        self.timeout = timeout

    # async def extract_content(self, url: str) -> str:
    #     page = await self.context.new_page()
    #     try:
    #         await page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)
    #         await asyncio.sleep(2)
    #         return await page.content()
    #     except Exception as e:
    #         logger.error(f"Error extracting content with Playwright: {e}")
    #         return ""
    #     finally:
    #         await page.close()

    async def extract_content(self, url: str) -> str:
        page = await self.context.new_page()
        try:
            try:
                await page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)
                await asyncio.sleep(2)
            except Exception as timeout_error:
                logger.warning(f"Timeout hoặc lỗi khi load trang {url}: {timeout_error}")

            content = await page.content()

            if not content or len(content.strip()) < 100:
                logger.warning(f"Nội dung trang {url} không đầy đủ (độ dài: {len(content)})")

            return content

        except Exception as e:
            logger.error(f"Error extracting content with Playwright {url}: {e}")
            try:
                return await page.content()
            except:
                return ""
        finally:
            await page.close()
