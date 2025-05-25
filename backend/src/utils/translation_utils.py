import time
import asyncio
from typing import Dict
from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor

class TranslationManager:
    def __init__(self, executor: ThreadPoolExecutor):
        self._executor = executor
        self._translation_cache: Dict[str, str] = {}

    async def translate_content_to_english(self, content: str) -> str:
        """Translate content to English with caching and error handling"""
        if not content or not content.strip():
            return content

        # Check cache first
        content_hash = str(hash(content))
        if content_hash in self._translation_cache:
            return self._translation_cache[content_hash]

        try:
            loop = asyncio.get_event_loop()
            translated = await loop.run_in_executor(
                self._executor,
                self._translate_text,
                content
            )

            self._translation_cache[content_hash] = translated
            return translated

        except Exception:
            return content

    def _translate_text(self, text: str) -> str:
        """Synchronous translation method for thread pool"""
        try:
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
                    time.sleep(0.1)

            return ' '.join(translated_chunks)

        except Exception:
            return text
