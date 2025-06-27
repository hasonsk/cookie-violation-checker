from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    APP_DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_TITLE: str = "Cookie Compliance Analyzer"
    API_DESCRIPTION: str = "API for analyzing cookie compliance and detecting violations."
    API_VERSION: str = "1.0.0"
    API_BASE: str = ""
    CORS_ORIGINS: str = ""

class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    DB_NAME: str
    USERS_COLLECTION: str = "users"
    WEBSITES_COLLECTION: str = "websites"
    POLICY_DISCOVERY_COLLECTION: str = "policy_discoveries"
    POLICY_CONTENTS_COLLECTION: str = "policy_contents"
    COOKIE_FEATURES_COLLECTION: str = "cookie_features"
    VIOLATIONS_COLLECTION: str = "cookie_violations"
    DOMAIN_REQUESTS_COLLECTION: str = "domain_requests" # Added for clarity and separation
    MONGODB_PWD: str
    MONGODB_USER: str = "username"
    MONGODB_CLUSTER: str = "cluster.mongodb.net"
    MONGODB_CONNECT_TIMEOUT_MS: int = 30000
    MONGODB_SOCKET_TIMEOUT_MS: int = 30000

    def get_mongodb_uri(self) -> str:
        """Generate MongoDB connection URI"""
        if not all([self.MONGODB_PWD, self.DB_NAME, self.MONGODB_USER]):
            raise ValueError("Missing required MongoDB environment variables")
        return f"mongodb+srv://{self.MONGODB_USER}:{self.MONGODB_PWD}@{self.MONGODB_CLUSTER}/{self.DB_NAME}?connectTimeoutMS={self.MONGODB_CONNECT_TIMEOUT_MS}&socketTimeoutMS={self.MONGODB_SOCKET_TIMEOUT_MS}"

class ExternalServicesSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    HF_TOKEN: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    TEMPERATURE: float = 0.7 # Default value, can be adjusted
    MAX_OUTPUT_TOKENS: int = 8192 # Default value, can be adjusted

    LLAMA_API_KEY: str = ""
    LLAMA_API_ENDPOINT: str = ""

class InternalAPISettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    REQUEST_TIMEOUT: int = 100
    MAX_RETRIES: int = 3
    MAX_CONCURRENT_REQUESTS: int = 10

class CrawlerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    CRAWLER_TIMEOUT: int = 30000 # milliseconds
    THREAD_POOL_MAX_WORKERS: int = 10

    # Browser configuration for Playwright
    BROWSER_HEADLESS: bool = True
    BROWSER_ARGS: list[str] = ['--no-sandbox', '--disable-dev-shm-usage']
    BROWSER_VIEWPORT_WIDTH: int = 1280
    BROWSER_VIEWPORT_HEIGHT: int = 800
    BROWSER_DEVICE_SCALE_FACTOR: int = 1
    BROWSER_EXTRA_HTTP_HEADERS: dict = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
    }

class PolicyDiscoverySettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    COOKIE_POLICY_PATTERNS: list[str] = [
        r'cookie[s]?\s*policy', r'cookie[s]?\s*notice', r'cookie[s]?\s*statement',
        r'cookie[s]?\s*information', r'cookie[s]?\s*settings', r'use\s*of\s*cookie[s]?',
        r'chính\s*sách\s*cookie[s]?', r'thông\s*báo\s*cookie[s]?', r'sử\s*dụng\s*cookie[s]?',
        r'quy\s*định\s*cookie[s]?', r'política\s*de\s*cookie[s]?', r'politique\s*de\s*cookie[s]?',
        r'cookie[s]?\s*richtlinie', r'informativa\s*cookie[s]?',
    ]
    URL_PATTERNS: list[str] = [
        r'/cookie[s]?[-_]?policy', r'/cookie[s]?[-_]?notice', r'/privacy.*cookie',
        r'/legal.*cookie', r'/cookie[s]?$',
    ]
    FOOTER_SELECTORS: list[str] = ['footer', '.footer', '.site-footer']
    NAV_SELECTORS: list[str] = ['nav', '.navigation', '.nav', '.menu']

class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    SYSTEM_PROMPT_LLAMA: str = """
You are a specialized AI system for extracting and structuring cookie declarations from website privacy policies and cookie notices.
Your task is to analyze the provided text and extract cookie information, then classify cookies into three distinct categories based on their specificity level.

CLASSIFICATION RULES
- specific: Clearly named cookies (e.g., _ga, _fbp) with at least one of the following attributes: purpose, retention, third_party, or behavior. These cookies must be technically identifiable.
- general: Cookie categories without specific names (e.g., "Marketing Cookies", "Necessary Cookies") described at a category level without exact technical details.
- undefined: Cookie mentions that are vague or ambiguous (e.g., "Cookies are used to improve our services") and cannot be classified into specific or general.

OUTPUT FORMAT: TYPE|name|attribute|value

ATTRIBUTES:
• purpose (required): Strictly Necessary, Functionality, Analytical, Targeting/Advertising/Marketing, Performance, Social Sharing
• retention: Exact timeframes ("2 years", "session", "persistent")
• third_party: Provider names ("Google, Facebook") or "First Party"
• behavior: How cookie works/stored/used

RULES:
- One attribute per line
- Skip undefined attributes
- No extra text outside output

EXAMPLE:
Input: "Cookie _ga lasts 2 years for Google Analytics traffic analysis. Marketing cookies show ads.Some cookies improve user experience."

Output:
specific|_ga|purpose|Analytical
specific|_ga|retention|2 years
specific|_ga|third_party|Google Analytics
specific|_ga|behavior|analyzes website traffic

general|Marketing cookies|purpose|Targeting/Advertising/Marketing
general|Marketing cookies|behavior|show personalized advertisements

undefined|cookies|behavior|improve user experience
"""
    SYSTEM_PROMPT_GEMINI: str = """
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

class ViolationSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    RETENTION_THRESHOLD_PERCENTAGE: float = 30.0
    SEMANTIC_SIMILARITY_THRESHOLD: float = 0.5
    LONG_TERM_RETENTION_DAYS: int = 365
    SESSION_THRESHOLD_HOURS: int = 24
    ISSUE_PENALTY_POINTS: int = 5
    MAX_COMPLIANCE_SCORE: int = 100
    KNOWN_AD_TRACKERS: list[str] = [
        'doubleclick.net', 'google-analytics.com', 'googletagmanager.com',
        'facebook.com', 'connect.facebook.net', 'twitter.com', 'linkedin.com',
        'amazon-adsystem.com', 'googlesyndication.com', 'adsystem.amazon.com',
        'youtube.com', 'googlevideo.com', 'hotjar.com', 'segment.com',
        'mixpanel.com', 'intercom.io', 'zendesk.com'
    ]
    STANDARD_PURPOSE_LABELS: list[str] = [
        "Strictly Necessary", "Functionality", "Analytical",
        "Targeting/Advertising/Marketing", "Performance", "Social Sharing"
    ]

class Settings:
    def __init__(self):
        self.app = AppSettings()
        self.db = DatabaseSettings()
        self.external = ExternalServicesSettings()
        self.internal_api = InternalAPISettings()
        self.crawler = CrawlerSettings()
        self.policy_discovery = PolicyDiscoverySettings()
        self.llm = LLMSettings() # Add LLMSettings
        self.violation = ViolationSettings()

settings = Settings()
