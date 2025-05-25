import re
import json
from urllib.parse import urlparse
from typing import Optional
import asyncio
import langdetect
from concurrent.futures import ThreadPoolExecutor

class TextProcessor:
    def __init__(self, executor: ThreadPoolExecutor):
        self._executor = executor

    async def extract_clean_text(self, html_content: str) -> str:
        """Extract and clean text content from HTML"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'lxml')

            # Remove unwanted elements
            for element in soup(['script', 'style', 'footer', 'header', 'nav',
                               'form', 'iframe', 'aside', 'meta', 'link', 'noscript']):
                element.decompose()

            # Get text content
            text = soup.get_text(separator=' ', strip=True)

            # Clean up the text
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'https?://\S+', '', text)
            text = re.sub(r'\S+@\S+', '', text)
            text = re.sub(r'[^\w\s.,;:!?()-]', '', text)

            return text.strip()

        except Exception as e:
            return ""

    async def detect_language_async(self, text: str) -> Optional[str]:
        """Async language detection"""
        if not text or len(text.strip()) < 50:
            return None

        try:
            loop = asyncio.get_event_loop()
            language = await loop.run_in_executor(
                self._executor,
                self._detect_language_sync,
                text[:1000]
            )
            return language
        except Exception:
            return None

    def _detect_language_sync(self, text: str) -> Optional[str]:
        """Synchronous language detection for thread pool"""
        try:
            return langdetect.detect(text)
        except:
            return None

def extract_domain(website_url: str) -> str:
    """Extract domain from URL"""
    try:
        parsed = urlparse(website_url)
        return parsed.netloc or parsed.path
    except:
        return website_url

def prepare_content(policy_content: str, table_content: Optional[str] = None) -> str:
    """Prepare content for AI analysis"""
    content_parts = []

    if policy_content and policy_content.strip():
        content_parts.append(f"Cookie policy: {policy_content}")

    if table_content and table_content.strip():
        content_parts.append(f"Table: {table_content}")

    if not content_parts:
        content_parts.append("No specific cookie policy content provided.")

    return "\n\n".join(content_parts)

def extract_json_from_response(response: str) -> str:
    """Extract JSON from AI response text"""
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        return json_match.group()
    return response
