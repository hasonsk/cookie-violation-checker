from typing import Optional
from loguru import logger

from src.schemas.cookie import PolicyCookieList
from src.services.cookie_extractor_service.interfaces.llm_provider import LLMProvider
from src.services.cookie_extractor_service.processors.content_analyzer import ContentAnalyzer
from src.services.cookie_extractor_service.processors.prompt_builder import PromptBuilder
from src.services.cookie_extractor_service.processors.response_processor import LLMResponseProcessor

class CookieExtractorService:
    def __init__(
        self,
        llm_provider: LLMProvider,
        content_analyzer: ContentAnalyzer,
        prompt_builder: PromptBuilder,
        response_processor: LLMResponseProcessor
    ):
        self.llm_provider = llm_provider
        self.content_analyzer = content_analyzer
        self.prompt_builder = prompt_builder
        self.response_processor = response_processor

    async def extract_cookie_features(
        self,
        original_content: Optional[str] = None,
        table_content: Optional[str] = None,
    ) -> PolicyCookieList:
        """
        Extract cookie features from policy content
        Single responsibility: orchestrate the cookie extraction workflow
        """
        # Step 1: Prepare content
        content_to_analyze, content_type = self.content_analyzer.prepare_content_for_analysis(
            original_content, table_content
        )

        if not content_to_analyze:
            return PolicyCookieList(is_specific=0, cookies=[])

        try:
            # Step 2: Build prompt
            prompt = self.prompt_builder.build_cookie_extraction_prompt(content_to_analyze)

            # Step 3: Get LLM response
            raw_response = await self.llm_provider.generate_content(prompt)
            logger.debug(f"LLM Raw Response from {self.llm_provider.get_provider_name()}: {raw_response}")

            # Step 4: Process response
            clean_response = self.response_processor.clean_json_response(raw_response)
            response_dict = self.response_processor.parse_json_response(clean_response)

            # Step 5: Convert to model
            policy_cookie_list = PolicyCookieList(**response_dict)
            logger.info(f"Successfully extracted cookie features using {self.llm_provider.get_provider_name()}")

            return policy_cookie_list

        except Exception as e:
            logger.error(f"Error during cookie feature extraction: {e}")
            return PolicyCookieList(is_specific=0, cookies=[])
