import re
from loguru import logger
import asyncio
from typing import List, Dict, Optional
from urllib.parse import urlparse, quote_plus, urljoin
from playwright.async_api import Browser, Page

class SearchService:
    """Service for finding cookie policies through search engines"""

    def __init__(self, browser: Browser):
        self.browser = browser

        # Enhanced cookie policy patterns for scoring search results
        self.cookie_policy_patterns = [
            r'cookie[s]?\s*policy',
            r'cookie[s]?\s*notice',
            r'cookie[s]?\s*statement',
            r'cookie[s]?\s*information',
            r'cookie[s]?\s*settings',
            r'cookie[s]?\s*preference[s]?',
            r'use\s*of\s*cookie[s]?',
            r'about\s*cookie[s]?',
            r'cookie[s]?\s*consent',
            r'cookie[s]?\s*management',
            # Vietnamese
            r'chính\s*sách\s*cookie[s]?',
            r'thông\s*báo\s*cookie[s]?',
            r'sử\s*dụng\s*cookie[s]?',
            # Spanish/Portuguese
            r'política\s*de\s*cookie[s]?',
            r'uso\s*de\s*cookie[s]?',
            # French
            r'politique\s*de\s*cookie[s]?',
            r'utilisation\s*de[s]?\s*cookie[s]?',
            # German
            r'cookie[s]?\s*richtlinie',
            r'cookie[s]?\s*verwendung',
            # Italian
            r'informativa\s*cookie[s]?',
            r'utilizzo\s*cookie[s]?',
        ]

        # URL path patterns that indicate cookie policy pages
        self.cookie_url_patterns = [
            r'cookie[s]?[-_]?policy',
            r'cookie[s]?[-_]?notice',
            r'cookie[s]?[-_]?statement',
            r'cookie[s]?[-_]?information',
            r'cookie[s]?[-_]?settings',
            r'cookie[s]?[-_]?consent',
            r'cookie[s]?[-_]?preference[s]?',
            r'use[-_]?of[-_]?cookie[s]?',
            r'about[-_]?cookie[s]?',
            r'cookie[s]?[-_]?management',
        ]

    def _extract_url_root(self, website_url: str) -> str:
        """Extract root URL from website URL"""
        parsed = urlparse(website_url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _is_valid_policy_url(self, policy_url: str, url_root: str) -> bool:
        """Check if policy URL meets the criteria"""
        if not policy_url or not url_root:
            return False

        # Check if policy_url contains url_root
        if url_root not in policy_url:
            return False

        # Check if policy_url contains cookie-related keywords
        policy_url_lower = policy_url.lower()

        # Check URL path for cookie keywords
        has_cookie_keyword = any(
            re.search(pattern, policy_url_lower)
            for pattern in self.cookie_url_patterns
        )

        # Also check for general "cookie" term
        if not has_cookie_keyword:
            has_cookie_keyword = 'cookie' in policy_url_lower

        return has_cookie_keyword

    async def search_policy_with_bing(self, website_url: str) -> Optional[str]:
        """Search for cookie policy using Bing search"""
        if not self.browser:
            logger.warning("Browser not available, skipping Bing search")
            return None

        try:
            logger.info(f"Searching policy with Bing for: {website_url}")

            # Extract domain and URL root
            parsed_url = urlparse(website_url)
            domain = parsed_url.netloc
            url_root = self._extract_url_root(website_url)

            # Skip localhost and local development URLs
            if 'localhost' in domain or '127.0.0.1' in domain or domain.startswith('192.168.'):
                logger.info(f"Skipping Bing search for local domain: {domain}")
                return None

            # Enhanced search queries with better targeting
            search_queries = [
                f'site:{domain} "cookie policy"',
                f'site:{domain} cookies',
                f'site:{domain} "use of cookies"',
            ]

            # Try each search query
            for query in search_queries:
                logger.info(f"Trying Bing search query: {query}")

                policy_url = await self._perform_bing_search(query, domain, url_root)
                if policy_url and self._is_valid_policy_url(policy_url, url_root):
                    logger.info(f"Found valid policy URL via Bing: {policy_url}")
                    return policy_url

                # Small delay between searches to avoid rate limiting
                await asyncio.sleep(1)

            logger.info("Bing search completed - no valid results found")
            return None

        except Exception as e:
            logger.error(f"Bing search error: {str(e)}")
            return None

    async def _perform_bing_search(self, query: str, domain: str, url_root: str) -> Optional[str]:
        """Perform a single Bing search query"""
        page = None
        try:
            # Check if browser is still available
            if not self.browser:
                logger.error("Browser is not available, cannot perform search")
                return None

            # Create new page with proper error handling
            try:
                page = await self.browser.new_page()
            except Exception as page_error:
                logger.error(f"Failed to create new page: {str(page_error)}")
                return None

            # Set a shorter timeout for page operations
            page.set_default_timeout(15000)  # 15 seconds

            # Set user agent and other headers
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            })

            # Navigate to Bing search with reduced timeout and better error handling
            encoded_query = quote_plus(query)
            search_url = f"https://www.bing.com/search?q={encoded_query}"

            logger.info(f"Navigating to: {search_url}")

            # Use a more reliable wait condition
            try:
                await page.goto(search_url, wait_until='domcontentloaded', timeout=15000)
            except Exception as nav_error:
                logger.error(f"Navigation failed: {str(nav_error)}")
                return None

            # Wait for search results to load with fallback
            try:
                await page.wait_for_selector('#b_results', timeout=8000)
            except Exception as selector_error:
                logger.warning(f"Results selector not found, trying alternative: {str(selector_error)}")
                # Try alternative selectors
                try:
                    await page.wait_for_selector('.b_searchResults', timeout=5000)
                except Exception:
                    logger.error("No search results container found")
                    return None

            # Extract search result links with better error handling
            try:
                results = await page.evaluate('''
                    () => {
                        const results = [];

                        // Try multiple selectors for search results
                        const selectors = [
                            '#b_results .b_algo h2 a',
                            '.b_searchResults .b_algo h2 a',
                            '#b_results .b_title a',
                            '.b_searchResults .b_title a',
                            '#b_results .b_algo .b_title a',
                            '.b_searchResults .b_algo .b_title a'
                        ];

                        let resultElements = [];
                        for (const selector of selectors) {
                            resultElements = document.querySelectorAll(selector);
                            if (resultElements.length > 0) break;
                        }

                        for (const element of resultElements) {
                            try {
                                const href = element.href;
                                const title = element.textContent || element.innerText || '';

                                if (href && href.startsWith('http')) {
                                    results.push({
                                        url: href,
                                        title: title.trim()
                                    });
                                }
                            } catch (e) {
                                console.log('Error processing element:', e);
                            }
                        }

                        return results;
                    }
                ''')
            except Exception as eval_error:
                logger.error(f"Error evaluating page: {str(eval_error)}")
                return None

            # Filter and rank results
            if results:
                logger.info(f"Found {len(results)} search results")
                policy_url = self._extract_policy_from_search_results(results, domain, url_root)
                return policy_url
            else:
                logger.info("No search results found")
                return None

        except Exception as e:
            logger.error(f"Error performing Bing search: {str(e)}")
            return None
        finally:
            if page:
                try:
                    await page.close()
                except Exception as close_error:
                    logger.warning(f"Error closing page: {str(close_error)}")

    def _extract_policy_from_search_results(self, results: List[Dict], domain: str, url_root: str) -> Optional[str]:
        """Extract the best cookie policy URL from search results with enhanced criteria checking"""
        scored_results = []

        for result in results:
            url = result.get('url', '')
            title = result.get('title', '')

            # First check: URL must contain url_root (domain)
            if url_root not in url:
                continue

            # Second check: URL must contain cookie-related keywords
            if not self._is_valid_policy_url(url, url_root):
                continue

            score = 0.0

            # Score based on URL patterns (higher weight for specific patterns)
            url_lower = url.lower()

            # High score for exact matches
            if any(re.search(f"/{pattern}/?$", url_lower) for pattern in self.cookie_url_patterns):
                score += 1.0
            elif any(re.search(f"/{pattern}/", url_lower) for pattern in self.cookie_url_patterns):
                score += 0.9
            elif any(re.search(pattern, url_lower) for pattern in self.cookie_url_patterns):
                score += 0.7

            # Bonus for common cookie policy URL patterns
            if re.search(r'cookie[s]?[-_]?policy', url_lower):
                score += 0.3
            elif 'cookie' in url_lower and 'policy' in url_lower:
                score += 0.2
            elif 'cookie' in url_lower:
                score += 0.1

            # Score based on title
            title_lower = title.lower()
            if any(re.search(pattern, title_lower) for pattern in self.cookie_policy_patterns):
                score += 0.4

            # Prefer shorter, cleaner URLs (typically better structured)
            path_segments = len([seg for seg in url.replace(url_root, '').split('/') if seg])
            if path_segments <= 2:
                score += 0.2
            elif path_segments <= 3:
                score += 0.1

            # Prefer HTTPS
            if url.startswith('https://'):
                score += 0.05

            # Bonus for exact domain match (not subdomain)
            if url.startswith(url_root + '/'):
                score += 0.1

            if score > 0:
                scored_results.append({
                    'url': url,
                    'score': score,
                    'title': title
                })

        # Sort by score and return the best match
        if scored_results:
            scored_results.sort(key=lambda x: x['score'], reverse=True)

            # Log all candidates for debugging
            for i, result in enumerate(scored_results[:5]):  # Top 5
                logger.info(f"Candidate {i+1}: {result['url']} (score: {result['score']:.2f})")

            best_result = scored_results[0]

            # Lower threshold since we now have stricter validation
            if best_result['score'] >= 0.1:
                logger.info(f"Selected policy URL: {best_result['url']} (score: {best_result['score']:.2f})")
                return best_result['url']
            else:
                logger.info(f"Best result score too low: {best_result['score']:.2f}")

        logger.info("No suitable policy URL found in search results")
        return None

    async def search_policy_with_google(self, website_url: str) -> Optional[str]:
        """Search for cookie policy using Google search (alternative method)"""
        if not self.browser:
            logger.warning("Browser not available, skipping Google search")
            return None

        try:
            logger.info(f"Searching policy with Google for: {website_url}")

            # Extract domain and URL root
            parsed_url = urlparse(website_url)
            domain = parsed_url.netloc
            url_root = self._extract_url_root(website_url)

            # Skip localhost and local development URLs
            if 'localhost' in domain or '127.0.0.1' in domain or domain.startswith('192.168.'):
                logger.info(f"Skipping Google search for local domain: {domain}")
                return None

            # Google search queries
            search_queries = [
                f'site:{domain} "cookie policy"',
                f'{domain} cookie policy',
            ]

            # Try each search query
            for query in search_queries:
                logger.info(f"Trying Google search query: {query}")

                policy_url = await self._perform_google_search(query, domain, url_root)
                if policy_url and self._is_valid_policy_url(policy_url, url_root):
                    logger.info(f"Found valid policy URL via Google: {policy_url}")
                    return policy_url

                # Small delay between searches
                await asyncio.sleep(1)

            logger.info("Google search completed - no valid results found")
            return None

        except Exception as e:
            logger.error(f"Google search error: {str(e)}")
            return None

    async def _perform_google_search(self, query: str, domain: str, url_root: str) -> Optional[str]:
        """Perform a single Google search query"""
        page = None
        try:
            page = await self.browser.new_page()
            page.set_default_timeout(15000)

            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            })

            encoded_query = quote_plus(query)
            search_url = f"https://www.google.com/search?q={encoded_query}"

            await page.goto(search_url, wait_until='domcontentloaded', timeout=15000)

            # Wait for search results
            try:
                await page.wait_for_selector('#search', timeout=8000)
            except Exception:
                await page.wait_for_selector('.g', timeout=5000)

            # Extract results
            results = await page.evaluate('''
                () => {
                    const results = [];
                    const elements = document.querySelectorAll('.g h3 a, .yuRUbf a');

                    for (const element of elements) {
                        try {
                            const href = element.href;
                            const title = element.textContent || '';

                            if (href && href.startsWith('http')) {
                                results.push({
                                    url: href,
                                    title: title.trim()
                                });
                            }
                        } catch (e) {
                            console.log('Error processing element:', e);
                        }
                    }

                    return results;
                }
            ''')

            if results:
                logger.info(f"Found {len(results)} Google search results")
                return self._extract_policy_from_search_results(results, domain, url_root)

            return None

        except Exception as e:
            logger.error(f"Error performing Google search: {str(e)}")
            return None
        finally:
            if page:
                try:
                    await page.close()
                except Exception:
                    pass
