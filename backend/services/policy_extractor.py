import asyncio
import json
import logging
import re
import time
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

import langdetect
from bs4 import BeautifulSoup, Tag
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from deep_translator import GoogleTranslator
from config.settings import get_settings
# from constants.policy_constants import (
#     COOKIE_POLICY_PAGE_TITLES,
#     COOKIE_POLICY_URL_KEYWORDS,
# )
# from exceptions.policy_exceptions import (
#     CrawlTimeoutError,
#     PolicyNotFoundException,
#     TranslationError,
#     WebsiteAccessError,
# )
# from utils.redis_cache import redis_cache

CRAWLER_USER_AGENT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
CRAWLER_TIMEOUT = 80
# Configure logginga
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TableData:
    """Data structure for extracted table information"""
    headers: List[str]
    rows: List[Dict[str, Any]]
    metadata: Dict[str, Any]


@dataclass
class PolicyContent:
    """Data structure for policy content"""
    website_url: str
    policy_url: Optional[str]
    original_content: str
    translated_content: Optional[str]
    detected_language: Optional[str]
    table_content: List[TableData]
    translated_table_content: Optional[str]
    error: Optional[str] = None


class ContentExtractor:
    """
    Optimized ContentExtractor for extracting and processing policy content.

    Key improvements:
    1. Better separation of concerns
    2. Async context management
    3. Enhanced error handling and retry logic
    4. Optimized translation handling
    5. Improved table extraction
    6. Better caching strategy
    """

    def __init__(self):
        """Initialize the ContentExtractor with optimized settings"""
        self.user_agent = CRAWLER_USER_AGENT
        self.timeout = CRAWLER_TIMEOUT

        # Browser context for reuse
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None

        # Translation cache to avoid redundant API calls
        self._translation_cache: Dict[str, str] = {}

        # Thread pool for CPU-intensive tasks
        self._executor = ThreadPoolExecutor(max_workers=4)

    async def __aenter__(self):
        """Async context manager entry"""
        await self._initialize_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._cleanup_browser()

    async def _initialize_browser(self):
        """Initialize browser context for reuse"""
        if not self._browser:
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            self._context = await self._browser.new_context(
                user_agent=self.user_agent,
                viewport={"width": 1280, "height": 800},
                device_scale_factor=1,
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                }
            )

    async def _cleanup_browser(self):
        """Cleanup browser resources"""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()

    async def extract_policy_content(
        self,
        website_url: str,
        policy_url: Optional[str] = None,
        translate_to_english: bool = True,
        force_refresh: bool = False
    ) -> PolicyContent:
        """
        Main method to extract policy content from a website

        Args:
            website_url: The main website URL
            policy_url: Optional specific policy URL (if known)
            translate_to_english: Whether to translate content to English
            force_refresh: Whether to bypass cache

        Returns:
            PolicyContent object with extracted data
        """
        try:
            # Check cache first
            if not force_refresh:
                cached_result = await self._get_cached_content(website_url)
                if cached_result:
                    logger.info(f"Cache hit for URL: {website_url}")
                    return cached_result

            # Initialize browser if not already done
            if not self._browser:
                await self._initialize_browser()

            if not policy_url:
                return PolicyContent(
                    website_url=website_url,
                    policy_url=None,
                    original_content="",
                    translated_content=None,
                    detected_language=None,
                    table_content=[],
                    translated_table_content=None,
                    error="Cookie policy URL not found"
                )

            # Extract content from policy page
            page_content = await self._extract_page_content(policy_url)

            # Process extracted content
            policy_content = await self._process_content(
                website_url=website_url,
                policy_url=policy_url,
                html_content=page_content,
                translate_to_english=translate_to_english
            )

            # Cache the result
            await self._cache_content(website_url, policy_content)

            return policy_content

        except Exception as e:
            logger.error(f"Error extracting policy content from {website_url}: {e}")
            return PolicyContent(
                website_url=website_url,
                policy_url=policy_url,
                original_content="",
                translated_content=None,
                detected_language=None,
                table_content=[],
                translated_table_content=None,
                error=str(e)
            )

    async def _extract_page_content(self, policy_url: str) -> str:
        """Extract HTML content from policy page with retry logic"""
        page = await self._context.new_page()

        try:
            # Try with networkidle first, fallback to domcontentloaded
            try:
                await page.goto(policy_url, wait_until="networkidle", timeout=self.timeout * 1000)
            except:
                logger.warning(f"Networkidle timeout for {policy_url}, trying domcontentloaded")
                await page.goto(policy_url, wait_until="domcontentloaded", timeout=self.timeout * 1000)

            # Wait for dynamic content to load
            await asyncio.sleep(2)

            return await page.content()

        except Exception as e:
            logger.error(f"Error extracting page content from {policy_url}: {e}")
            # raise WebsiteAccessError(f"Cannot access policy page: {policy_url}")
        finally:
            await page.close()

    async def _process_content(
        self,
        website_url: str,
        policy_url: str,
        html_content: str,
        translate_to_english: bool = True
    ) -> PolicyContent:
        """Process extracted HTML content into structured data"""

        # Extract text content
        policy_text = await self._extract_clean_text(html_content)

        # Detect language
        detected_language = await self._detect_language_async(policy_text)

        # Extract tables
        table_data = await self.extract_tables_from_page_html(html_content)

        # Handle translation
        translated_text = None
        translated_table_content = None

        if translate_to_english and detected_language and detected_language != 'en':
            translated_text = await self.translate_content_to_english(policy_text)

            if table_data:
                table_json = json.dumps([table.__dict__ for table in table_data], ensure_ascii=False, indent=2)
                translated_table_content = await self.translate_content_to_english(table_json)

        # Convert table data to JSON string for storage
        table_content_str = None
        if table_data:
            table_content_str = json.dumps([table.__dict__ for table in table_data], ensure_ascii=False, indent=2)

        return PolicyContent(
            website_url=website_url,
            policy_url=policy_url,
            original_content=policy_text,
            translated_content=translated_text,
            detected_language=detected_language,
            table_content=table_data,
            translated_table_content=translated_table_content
        )

    async def extract_tables_from_page_html(self, html_content: str) -> List[TableData]:
        """Extract and structure table data from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            tables = soup.find_all('table')
            extracted_tables = []

            logger.info(f"Found {len(tables)} tables in HTML content")

            for i, table in enumerate(tables):
                try:
                    # Extract headers
                    headers = self._extract_table_headers(table)
                    if not headers:
                        continue

                    # Extract rows
                    rows = self._extract_table_rows(table, headers)
                    if not rows:
                        continue

                    # Filter out rows that are likely headers or empty
                    valid_rows = [row for row in rows if self._is_valid_data_row(row)]

                    if valid_rows:
                        table_data = TableData(
                            headers=headers,
                            rows=valid_rows,
                            metadata={
                                "table_index": i,
                                "row_count": len(valid_rows),
                                "column_count": len(headers),
                                "has_cookie_data": self._detect_cookie_table(headers, valid_rows)
                            }
                        )
                        extracted_tables.append(table_data)

                except Exception as e:
                    logger.debug(f"Error processing table {i}: {e}")
                    continue

            return extracted_tables

        except Exception as e:
            logger.error(f"Error extracting tables: {e}")
            return []

    def _extract_table_headers(self, table: Tag) -> List[str]:
        """Extract headers from table with improved logic"""
        headers = []

        # Try thead first
        thead = table.find('thead')
        if thead:
            header_row = thead.find('tr')
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]

        # If no thead, try first row with th elements
        if not headers:
            first_row = table.find('tr')
            if first_row and first_row.find_all('th'):
                headers = [th.get_text(strip=True) for th in first_row.find_all('th')]

        # If still no headers, use first row as headers if it looks like headers
        if not headers:
            first_row = table.find('tr')
            if first_row:
                potential_headers = [td.get_text(strip=True) for td in first_row.find_all('td')]
                if self._looks_like_headers(potential_headers):
                    headers = potential_headers

        return [h for h in headers if h]  # Filter out empty headers

    def _extract_table_rows(self, table: Tag, headers: List[str]) -> List[Dict[str, str]]:
        """Extract data rows from table"""
        rows = []
        all_rows = table.find_all('tr')

        # Skip header row
        data_rows = all_rows[1:] if len(all_rows) > 1 else all_rows

        for row in data_rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) == len(headers):
                row_data = {}
                for i, cell in enumerate(cells):
                    if i < len(headers):
                        row_data[headers[i]] = cell.get_text(strip=True)
                rows.append(row_data)

        return rows

    def _looks_like_headers(self, potential_headers: List[str]) -> bool:
        """Determine if a list of strings looks like table headers"""
        if not potential_headers:
            return False

        header_indicators = ['name', 'purpose', 'type', 'duration', 'cookie', 'description', 'category']
        return any(any(indicator in header.lower() for indicator in header_indicators)
                  for header in potential_headers)

    def _is_valid_data_row(self, row: Dict[str, str]) -> bool:
        """Check if a row contains valid data (not empty or header-like)"""
        if not row:
            return False

        # Check if row has meaningful content
        non_empty_values = [v for v in row.values() if v.strip()]
        if len(non_empty_values) < len(row) * 0.5:  # At least 50% non-empty
            return False

        # Check if it's not a repeated header
        values_lower = [v.lower() for v in row.values()]
        header_indicators = ['name', 'purpose', 'type', 'duration', 'cookie']
        header_like = sum(1 for indicator in header_indicators
                         for value in values_lower if indicator in value)

        return header_like < len(row) * 0.3  # Less than 30% header-like content

    def _detect_cookie_table(self, headers: List[str], rows: List[Dict[str, str]]) -> bool:
        """Detect if table contains cookie information"""
        cookie_indicators = ['cookie', 'name', 'purpose', 'duration', 'expiry', 'type', 'category']

        # Check headers
        header_matches = sum(1 for header in headers
                           for indicator in cookie_indicators
                           if indicator in header.lower())

        # Check data content
        data_matches = 0
        for row in rows[:5]:  # Check first 5 rows
            for value in row.values():
                if any(indicator in value.lower() for indicator in ['cookie', '_ga', '_gid', 'session']):
                    data_matches += 1
                    break

        return header_matches >= 2 or data_matches >= 2

    async def translate_content_to_english(self, content: str) -> str:
        """
        Translate content to English with caching and error handling
        """
        if not content or not content.strip():
            return content

        # Check cache first
        content_hash = str(hash(content))
        if content_hash in self._translation_cache:
            return self._translation_cache[content_hash]

        try:
            # Use thread pool for translation to avoid blocking
            loop = asyncio.get_event_loop()
            translated = await loop.run_in_executor(
                self._executor,
                self._translate_text,
                content
            )

            # Cache the result
            self._translation_cache[content_hash] = translated
            return translated

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return content  # Return original if translation fails

    def _translate_text(self, text: str) -> str:
        """Synchronous translation method for thread pool"""
        try:
            # Split long text into chunks to avoid API limits
            max_chunk_size = 4000
            if len(text) <= max_chunk_size:
                return GoogleTranslator(source='auto', target='en').translate(text)

            # Handle long text by splitting into chunks
            chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
            translated_chunks = []

            for chunk in chunks:
                if chunk.strip():
                    translated = GoogleTranslator(source='auto', target='en').translate(chunk)
                    translated_chunks.append(translated)
                    time.sleep(0.1)  # Small delay to avoid rate limiting

            return ' '.join(translated_chunks)

        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text

    async def _extract_clean_text(self, html_content: str) -> str:
        """Extract and clean text content from HTML"""
        try:
            soup = BeautifulSoup(html_content, 'lxml')

            # Remove unwanted elements
            for element in soup(['script', 'style', 'footer', 'header', 'nav',
                               'form', 'iframe', 'aside', 'meta', 'link', 'noscript']):
                element.decompose()

            # Get text content
            text = soup.get_text(separator=' ', strip=True)

            # Clean up the text
            # Remove multiple whitespaces
            text = re.sub(r'\s+', ' ', text)

            # Remove URLs
            text = re.sub(r'https?://\S+', '', text)

            # Remove email addresses
            text = re.sub(r'\S+@\S+', '', text)

            # Remove excessive punctuation
            text = re.sub(r'[^\w\s.,;:!?()-]', '', text)

            return text.strip()

        except Exception as e:
            logger.error(f"Error extracting clean text: {e}")
            return ""

    async def _detect_language_async(self, text: str) -> Optional[str]:
        """Async language detection"""
        if not text or len(text.strip()) < 50:
            return None

        try:
            loop = asyncio.get_event_loop()
            language = await loop.run_in_executor(
                self._executor,
                self._detect_language_sync,
                text[:1000]  # Use first 1000 chars for detection
            )
            return language
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return None

    def _detect_language_sync(self, text: str) -> Optional[str]:
        """Synchronous language detection for thread pool"""
        try:
            return langdetect.detect(text)
        except:
            return None

    async def _get_cached_content(self, website_url: str) -> Optional[PolicyContent]:
        """Get cached policy content"""
        try:
            cache_key = f"policy_content:{website_url}"
            cached_data = await redis_cache.get(cache_key, as_json=True)
            if cached_data:
                # Convert cached data back to PolicyContent object
                return PolicyContent(**cached_data)
            return None
        except Exception as e:
            logger.error(f"Error getting cached content: {e}")
            return None

    async def _cache_content(self, website_url: str, content: PolicyContent):
        """Cache policy content"""
        try:
            cache_key = f"policy_content:{website_url}"
            # Convert PolicyContent to dict for caching
            cache_data = {
                'website_url': content.website_url,
                'policy_url': content.policy_url,
                'original_content': content.original_content,
                'translated_content': content.translated_content,
                'detected_language': content.detected_language,
                'table_content': [table.__dict__ for table in content.table_content],
                'translated_table_content': content.translated_table_content,
                'error': content.error
            }
            await redis_cache.set(cache_key, cache_data, ttl=3600 * 24)  # Cache for 24 hours
        except Exception as e:
            logger.error(f"Error caching content: {e}")


# Usage example and factory function
async def create_content_extractor() -> ContentExtractor:
    """Factory function to create and initialize ContentExtractor"""
    extractor = ContentExtractor()
    await extractor._initialize_browser()
    return extractor


# Example usage
async def main():
    """Example usage of the ContentExtractor"""
    async with ContentExtractor() as extractor:
        result = await extractor.extract_policy_content(
            website_url="https://stackoverflow.com/legal/cookie-policy",
            policy_url="https://www.ef.com.vn/legal/cookie-policy/",
            translate_to_english=True,
            force_refresh=False
        )

        # Convert to required output format
        output = {
            "website_url": result.website_url,
            "policy_url": result.policy_url,
            "original_content": result.original_content,
            "translated_content": result.translated_content,
            "detected_language": result.detected_language,
            "table_content": [table.__dict__ for table in result.table_content],
            "translated_table_content": result.translated_table_content,
            "error": result.error
        }

        print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
    # python -m services.policy_extractor

# https://www.allianz.fr/assurance-particulier/utilisation-des-cookies.html  Just a moment... www.allianz.fr Verifying you are human. This may take a few seconds. www.allianz.fr needs to review the security of your connection before proceeding. Verification successful Waiting for www.allianz.fr to respond... Ray ID: 943966bddbc5ddc9 Performance  security by Cloudflare
# Attention Required!  Cloudflare Please enable cookies. Sorry, you have been blocked You are unable to access prod-bbth-sweatybetty-com.cc-ecdn.net Why have I been blocked? This website is using a security service to protect itself from online attacks. The action you just performed triggered the security solution. There are several actions that could trigger this block including submitting a certain word or phrase, a SQL command or malformed data. What can I do to resolve this? You can email the site owner to let them know you were blocked. Please include what you were doing when this page came up and the Cloudflare Ray ID found at the bottom of this page. Cloudflare Ray ID: 943962e97aa30399  Your IP: Click to reveal 118.70.98.163  Performance  security by Cloudflar
