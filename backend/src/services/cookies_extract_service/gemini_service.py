import logging
from google import genai
from google.genai import types
from configs.cookie_extract_conf import cookie_extract_conf as settings

logger = logging.getLogger(__name__)

class GeminiService:
    """Service for interacting with Google Gemini AI"""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be provided or set as environment variable")

    async def generate_content(self, content: str) -> str:
        """Generate response using Gemini API"""
        try:
            # Create the model client
            client = genai.Client(api_key=self.api_key)

            # Prepare the prompt
            prompt = f"{settings.SYSTEM_PROMPT}\n\nContent to analyze:\n{content}"

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
                    temperature=settings.TEMPERATURE,
                    max_output_tokens=settings.MAX_OUTPUT_TOKENS,
                )
            )

            return response.text if response.text else '{"is_specific": 0, "cookies": []}'

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return '{"is_specific": 0, "cookies": []}'
