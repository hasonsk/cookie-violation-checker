import os
from dotenv import dotenv_values

class CookiesExtractConfig:
    """Application settings and configuration"""

    def __init__(self):
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBpPwWeKxESlPQQMA6qo8AtcVb-yyA3LSc")
        self.GEMINI_MODEL = "gemini-1.5-flash"
        self.TEMPERATURE = 0.1
        self.MAX_OUTPUT_TOKENS = 2048

        # System prompt for cookie extraction
        self.SYSTEM_PROMPT = """
ROLE: You are a cookie policy analysis expert.
Your task is to read a cookie policy text and extract detailed information about each cookie mentioned in that policy.

RESPONSE Format: Return ONLY a valid JSON object with this exact structure:
{
  "is_specific": 1,
  "cookies": [
    {
      "cookie_name": "cookie_name",
      "declared_purpose": "declared_purpose",
      "declared_retention": "declared_retention",
      "declared_third_parties": ["declared_third_parties"],
      "declared_description": "declared_description"
    }
  ]
}

If no specific cookies are described, return:
{
  "is_specific": 0,
  "cookies": []
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
"""

cookie_extract_conf = CookiesExtractConfig()
