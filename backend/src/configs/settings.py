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

class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    DB_NAME: str
    USERS_COLLECTION: str = "users"
    ROLE_CHANGE_REQUESTS_COLLECTION: str = "role_change_requests"
    POLICY_DISCOVERY_COLLECTION: str = "policy_discoveries"
    POLICY_CONTENTS_COLLECTION: str = "policy_contents"
    COOKIE_FEATURES_COLLECTION: str = "cookie_features"
    VIOLATIONS_COLLECTION: str = "cookie_violations"
    MONGODB_PWD: str
    MONGODB_USER: str = "username"
    MONGODB_CLUSTER: str = "cluster.mongodb.net"
    MONGODB_CONNECT_TIMEOUT_MS: int = 10000
    MONGODB_SOCKET_TIMEOUT_MS: int = 10000

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
    GEMINI_TEMPERATURE: float = 0.7 # Default value, can be adjusted
    GEMINI_MAX_OUTPUT_TOKENS: int = 8192 # Default value, can be adjusted

class InternalAPISettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    API_BASE: str
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

class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    REDIS_URL: str = "redis://localhost:6379"
    REDIS_TTL: int = 3600 # seconds

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
        self.redis = RedisSettings()
        self.violation = ViolationSettings()

settings = Settings()
