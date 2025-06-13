from src.schemas.policy import PolicyContent
from src.utils.table_extractor import TableExtractor
from src.utils.text_processing import TextProcessor
from src.utils.translation_utils import TranslationManager


class ContentProcessor:

    def __init__(self, text_processor: TextProcessor,
                 translation_manager: TranslationManager,
                 table_extractor: TableExtractor):
        self.text_processor = text_processor
        self.translation_manager = translation_manager
        self.table_extractor = table_extractor

    async def process_content(self, website_url: str, policy_url: str,
                            html_content: str, translate_to_english: bool = True) -> PolicyContent:

        # Extract text content
        policy_text = await self.text_processor.extract_clean_text(html_content)

        # Detect language
        detected_language = await self.text_processor.detect_language_async(policy_text)

        # Extract tables
        table_data = self.table_extractor.extract_tables_from_html(html_content)

        # Handle translation
        translated_text = None
        translated_table_content = None

        if translate_to_english and detected_language and detected_language != 'en':
            translated_text = await self.translation_manager.translate_content_to_english(policy_text)

            if table_data:
                import json
                table_json = json.dumps([table for table in table_data], ensure_ascii=False, indent=2)
                translated_table_content = await self.translation_manager.translate_content_to_english(table_json)

        return PolicyContent(
            website_url=website_url,
            policy_url=policy_url,
            original_content=policy_text,
            translated_content=translated_text,
            detected_language=detected_language,
            table_content=table_data,
            translated_table_content=translated_table_content
        )
