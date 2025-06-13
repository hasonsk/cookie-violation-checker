from typing import Optional, List, Dict, Any
from loguru import logger
import json

from src.configs.settings import settings
from src.schemas.cookie import PolicyCookieList
from src.schemas.policy import PolicyContent

from google import genai
from google.genai import types

SYSTEM_PROMPT = """
ROLE: You are a highly specialized AI for extracting and classifying cookie declarations from website cookie policies. Your task is to analyze the input text and return structured data as a valid JSON object following the exact schema below.

Your Capabilities
- Accurate Extraction: Capture all explicit and implied cookie-related data.
- Detailed Identification: Extract cookie names, purposes, retention periods, third-party associations, and behavior descriptions.
- Code-Ready Output: Return a syntactically correct and programmatically usable JSON object.

Output is a JSON object:
{
  "type": "object",
  "properties": {
    "is_specific": {
      "type": "integer",
      "enum": [0, 1]
    },
    "cookies": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "cookie_name": {
            "type": "string"
          },
          "declared_purpose": {
            "type": "string"
          },
          "declared_retention": {
            "type": ["string", "null"]
          },
          "declared_third_parties": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "declared_description": {
            "type": "string"
          }
        },
        "required": [
          "cookie_name",
          "declared_purpose",
          "declared_retention",
          "declared_third_parties",
          "declared_description"
        ]
      }
    }
  },
  "required": ["is_specific", "cookies"]
}

Specific Requirements:
1. Read and Analyze the Text: Carefully read the entire content to understand cookie types, purposes, storage duration, and ownership.

2. Extract Information for Each Cookie:
   - "cookie_name": Technical or descriptive name exactly as mentioned
   - "declared_purpose": Choose from: "Strictly Necessary", "Functionality", "Analytical", "Targeting/Advertising/Marketing", "Performance", "Social Sharing", or null
   - "declared_retention": Duration (e.g., "6 months", "24 hours", "Session", "Persistent", "Until deleted")
   - "declared_third_parties": Array of third parties, use ["First Party"] for first-party cookies
   - "declared_description": Direct content from text without fabrication

3. Set is_specific to 1 if specific cookies are found, 0 if only general descriptions exist.

IMPORTANT: Return ONLY valid JSON, no additional text or explanations.

Example output:
{
  "is_specific": 1,
  "cookies": [
    {
      "cookie_name": "_ga",
      "declared_purpose": "Analytical",
      "declared_retention": "24 hours",
      "declared_third_parties": ["Google"],
      "declared_description": "_ga cookie is used for Analytical"
    }
  ]
}

If no specific cookies are described, return:
{
  "is_specific": 0,
  "cookies": []
}
"""

class GeminiService:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key if api_key else settings.external.GEMINI_API_KEY
        self.model = model if model else settings.external.GEMINI_MODEL

        if not self.api_key:
            logger.error("GEMINI_API_KEY must be provided or set as environment variable")
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
                    temperature=settings.external.GEMINI_TEMPERATURE,
                    max_output_tokens=settings.external.GEMINI_MAX_OUTPUT_TOKENS,
                )
            )

            return response.text if response.text else '{"is_specific": 0, "cookies": []}'

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return '{"is_specific": 0, "cookies": []}'

class PolicyLLMService:
    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service

    async def extract_cookie_features(
        self,
        original_content: Optional[str] = None,
        table_content: Optional[str] = None,
    ) -> PolicyCookieList:
        """
        Extracts cookie features from policy content using the Gemini LLM.
        Prioritizes table content if available, otherwise uses original content.
        """
        content_to_analyze = ""
        if table_content:
            content_to_analyze = table_content
            logger.info("Analyzing table content for cookie features.")
        elif original_content:
            content_to_analyze = original_content
            logger.info("Analyzing original content for cookie features.")
        else:
            logger.warning("No content provided for cookie feature extraction.")
            return PolicyCookieList(is_specific=0, cookies=[])

        if not content_to_analyze.strip():
            logger.warning("Content to analyze is empty after stripping whitespace.")
            return PolicyCookieList(is_specific=0, cookies=[])

        try:
            llm_response_json_str = await self.gemini_service.generate_content(content_to_analyze)
            logger.debug(f"LLM Raw Response: {llm_response_json_str}")

            # Remove leading ```json if present in the response
            if llm_response_json_str.startswith("```json"):
              llm_response_json_str = llm_response_json_str[7:].strip()

            # Remove trailing ``` if present in the response
            if llm_response_json_str.endswith("```"):
              llm_response_json_str = llm_response_json_str[:-3].strip()

            # Parse the JSON string into a dictionary
            llm_response_dict = json.loads(llm_response_json_str)

            # Validate and convert to PolicyCookieList Pydantic model
            policy_cookie_list = PolicyCookieList(**llm_response_dict)
            logger.info("Successfully extracted cookie features using LLM.")
            return policy_cookie_list

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from LLM response: {e}. Response: {llm_response_json_str}")
            return PolicyCookieList(is_specific=0, cookies=[])
        except Exception as e:
            logger.error(f"Error during cookie feature extraction: {e}")
            return PolicyCookieList(is_specific=0, cookies=[])
