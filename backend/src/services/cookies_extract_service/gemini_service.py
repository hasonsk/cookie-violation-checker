from typing import Optional
from loguru import logger
from google import genai
from google.genai import types
from src.configs.cookie_extract_conf import SYSTEM_PROMPT, GEMINI_TEMPERATURE, GEMINI_MAX_OUTPUT_TOKENS

class GeminiService:
    def __init__(self, api_key:  Optional[str] = None, model:  Optional[str] = None):
        self.api_key = api_key
        self.model = model

        if not self.api_key:
            logger.info(self.api_key)
            raise ValueError("GEMINI_API_KEY must be provided or set as environment variable")

    async def generate_content(self, content: str) -> str:
        try:
            # Create the model client
            client = genai.Client(api_key=self.api_key)

            # Prepare the prompt
            prompt = f"{SYSTEM_PROMPT}\n\nContent to analyze:\n{content}"

            # Generate content
            response = client.models.generate_content(
                model=self.model,
                contents=[
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)]
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=GEMINI_TEMPERATURE,
                    max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
                )
            )

            return response.text if response.text else '{"is_specific": 0, "cookies": []}'

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return '{"is_specific": 0, "cookies": []}'
