from pydantic import BaseModel, Field

class APIConfig(BaseModel):
    api_base: str = Field(..., env="API_BASE")
    request_timeout: float = Field(30.0, env="REQUEST_TIMEOUT")
    max_retries: int = Field(3, env="MAX_RETRIES")
    max_concurrent_requests: int = Field(10, env="MAX_CONCURRENT_REQUESTS")
