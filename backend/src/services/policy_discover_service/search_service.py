import logging
import asyncio
from typing import Optional
from urllib.parse import urlparse

from utils.url_utils import extract_domain

logger = logging.getLogger(__name__)

class SearchService:
    """Service for searching policies using external APIs"""

    async def search_policy_with_bing(self, website_url: str) -> Optional[str]:
        """Search for cookie policy using Bing API"""
        try:
            logger.info(f"Searching policy with Bing for: {website_url}")

            domain = extract_domain(website_url)
            search_queries = [
                f'site:{domain} "cookie policy"',
                f'site:{domain} "privacy policy" cookies',
                f'site:{domain} "use of cookies"'
            ]

            # Mock implementation - replace with actual Bing Search API
            await asyncio.sleep(0.1)  # Simulate API delay

            # Return mock result for demonstration
            if 'example.com' in website_url:
                return f"{website_url.rstrip('/')}/cookie-policy"

            logger.info("Bing search completed - no results found")
            return None

        except Exception as e:
            logger.error(f"Bing search error: {str(e)}")
            return None

    # async def search_policy_with_bing(self, website_url: str) -> Optional[str]:
    #     """Tìm kiếm cookie policy của website trên Bing - tối ưu hóa cho Playwright"""
    #     page = None
    #     try:
    #         # page = await self.browser.new_page()
    #         page = await self.playwright.chromium.launch().new_page()

    #         # Tắt các resource không cần thiết để tăng tốc
    #         await page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2}", lambda route: route.abort())

    #         search_query = f"{website_url} cookie policy OR cookie notice"
    #         search_url = f"https://www.bing.com/search?q={search_query}"

    #         # Navigate với timeout tối ưu
    #         await page.goto(search_url, wait_until='networkidle', timeout=15000)

    #         # Chờ kết quả tìm kiếm load
    #         try:
    #             await page.wait_for_selector('.b_algo h2 a', timeout=10000)
    #         except:
    #             return None

    #         # Extract và xử lý kết quả bằng một lần evaluate duy nhất
    #         cookie_policy_url = await page.evaluate('''
    #             (website_url, cookieKeywords) => {
    #                 const results = document.querySelectorAll('.b_algo h2 a');

    #                 for (let i = 0; i < Math.min(3, results.length); i++) {
    #                     const elem = results[i];
    #                     const href = elem.href || '';
    #                     const text = elem.textContent?.toLowerCase() || '';

    #                     // Check cookie keywords
    #                     const isCookiePolicy = cookieKeywords.some(keyword =>
    #                         href.toLowerCase().includes(keyword) || text.includes(keyword)
    #                     );

    #                     if (isCookiePolicy) {
    #                         try {
    #                             const url = new URL(href);
    #                             const resultDomain = url.hostname;
    #                             // Kiểm tra domain match
    #                             if (resultDomain.includes(website_url) ||
    #                                 resultDomain.endsWith('.' + website_url) ||
    #                                 website_url.includes(resultDomain)) {
    #                                 return href;
    #                             }
    #                         } catch (e) {
    #                             continue;
    #                         }
    #                     }
    #                 }
    #                 return null;
    #             }
    #         ''', website_url, ['cookie', 'privacy', 'policy', 'cookies', 'gdpr'])

    #         return cookie_policy_url

    #     except Exception as e:
    #         print(f"Error searching Bing for {website_url}: {e}")
    #         return None
    #     finally:
    #         if page:
    #             await page.close()
