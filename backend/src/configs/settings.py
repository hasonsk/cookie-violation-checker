import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional, Dict, Any

# ==============================================================================
# CONFIGURATION SETTINGS
# ==============================================================================

class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""

    # API Configuration
    api_title: str = Field(default="Cookie Violations Check API", description="API title")
    api_version: str = Field(default="1.0.0", description="API version")
    api_description: str = Field(
        default="API for detecting cookie policy violations between declared policies and actual cookie collection",
        description="API description"
    )
    debug: bool = Field(default=True, description="Debug mode") # Set to False in production

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=1, description="Number of worker processes")

    # Database Configuration (MongoDB)
    mongodb_url: str = Field(default="mongodb://localhost:27017", description="MongoDB connection URL")
    mongodb_database: str = Field(default="cookie_violations", description="MongoDB database name")

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", description="Redis connection URL")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_ttl: int = Field(default=3600, description="Redis TTL in seconds")

    # Celery Configuration
    celery_broker_url: str = Field(default="redis://localhost:6379/0", description="Celery broker URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/0", description="Celery result backend URL")

    # External Services
    bing_api_key: Optional[str] = Field(default=None, description="Bing Search API key")
    gemini_api_key: Optional[str] = Field(default=None, description="Gemini API key")

    # Playwright Configuration
    playwright_timeout: int = Field(default=30000, description="Playwright timeout in milliseconds")
    playwright_headless: bool = Field(default=True, description="Run Playwright in headless mode")

    # Processing Configuration
    max_concurrent_tasks: int = Field(default=10, description="Maximum concurrent analysis tasks")
    task_timeout: int = Field(default=300, description="Task timeout in seconds")
    retry_count: int = Field(default=3, description="Number of retries for failed tasks")
    retry_backoff: float = Field(default=1.5, description="Retry backoff multiplier")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, description="Requests per minute limit")
    rate_limit_burst: int = Field(default=10, description="Rate limit burst size")

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )

    # Crawler Configuration
    crawler_user_agent: str = Field(
        default="Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        description="User-Agent string for the web crawler"
    )
    crawler_timeout: int = Field(
        default=60,
        description="Default timeout for web crawling requests in seconds"
    )

    # Security
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "chrome-extension://*"],
        description="CORS allowed origins"
    )
    api_key_header: str = Field(default="X-API-Key", description="API key header name")

    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()

def get_mongodb_connection_string() -> str:
    """Build MongoDB connection string from configuration."""
    settings = get_settings()
    return f"{settings.mongodb_url}/{settings.mongodb_database}"

def get_redis_connection_string() -> str:
    """Build Redis connection string from configuration."""
    settings = get_settings()
    return f"{settings.redis_url}/{settings.redis_db}"

def validate_environment():
    """Validate required environment variables."""
    settings = get_settings()

    if not settings.debug:
        # In production, require API keys
        if not settings.bing_api_key:
            raise ValueError("BING_API_KEY is required in production mode")
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required in production mode")

    # Validate MongoDB connection string
    if not settings.mongodb_url:
        raise ValueError("MONGODB_URL is required")

    # Validate Redis connection string
    if not settings.redis_url:
        raise ValueError("REDIS_URL is required")
