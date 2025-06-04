from typing import Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from contextlib import asynccontextmanager
from enum import Enum
from loguru import logger
from configs.api_conf import APIConfig
from schemas.analysis_schema import AnalysisPhase
from exceptions.custom_exceptions import RetryableError, PolicyAnalysisError

class InternalAPIClient:
    def __init__(self, config: APIConfig):
        self.config = config
        self._client_limits = httpx.Limits(
            max_keepalive_connections=20,
            max_connections=self.config.max_concurrent_requests,
            keepalive_expiry=30.0
        )

    @asynccontextmanager
    async def get_client(self):
        """Get HTTP client with proper configuration"""
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(self.config.request_timeout),
            limits=self._client_limits,
            follow_redirects=True
        ) as client:
            yield client

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(RetryableError)
    )
    async def post(
        self,
        client: httpx.AsyncClient,
        endpoint: str,
        payload: Dict[str, Any],
        phase: AnalysisPhase,
        request_id: str
    ) -> Dict[str, Any]:
        """Make HTTP POST request with retry logic and proper error handling"""
        url = f"{self.config.api_base}{endpoint}"

        try:
            response = await client.post(url, json=payload)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Rate limited
                logger.warning("rate_limited", endpoint=endpoint, request_id=request_id)
                raise RetryableError("Rate limited")
            elif 500 <= response.status_code < 600:  # Server errors
                logger.error("server_error",
                                  endpoint=endpoint,
                                  status_code=response.status_code,
                                  request_id=request_id)
                raise RetryableError(f"Server error: {response.status_code}")
            else:  # Client errors (4xx)
                error_detail = "Unknown client error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", error_detail)
                except:
                    pass

                raise PolicyAnalysisError(
                    phase=phase,
                    message=error_detail,
                    status_code=response.status_code
                )

        except httpx.TimeoutException:
            logger.error("request_timeout", endpoint=endpoint, request_id=request_id)
            raise RetryableError("Request timeout")
        except httpx.NetworkError as e:
            logger.error("network_error", endpoint=endpoint, error=str(e), request_id=request_id)
            raise RetryableError(f"Network error: {str(e)}")
