import uuid
from typing import Dict, List, Optional, Any
from backend.src.schemas.cookie_schema import CookieSubmissionRequest
import structlog
import httpx
from fastapi import HTTPException
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from contextlib import asynccontextmanager
import time
from enum import Enum

# Configuration
class APIConfig(BaseModel):
    api_base: str = Field(..., env="API_BASE")
    request_timeout: float = Field(30.0, env="REQUEST_TIMEOUT")
    max_retries: int = Field(3, env="MAX_RETRIES")
    max_concurrent_requests: int = Field(10, env="MAX_CONCURRENT_REQUESTS")

config = APIConfig()


class AnalysisPhase(Enum):
    DISCOVERY = "policy_discovery"
    EXTRACTION = "content_extraction"
    FEATURE_EXTRACTION = "feature_extraction"
    COMPLIANCE_CHECK = "compliance_check"

class AnalysisResult(BaseModel):
    total_issues: int
    compliance_score: float
    policy_cookies_count: int
    actual_cookies_count: int
    statistics: Dict[str, Any]
    issues: List[Dict[str, Any]]
    execution_time: float
    request_id: str

# Custom Exceptions
class PolicyAnalysisError(Exception):
    def __init__(self, phase: AnalysisPhase, message: str, status_code: int = 500):
        self.phase = phase
        self.message = message
        self.status_code = status_code
        super().__init__(f"[{phase.value}] {message}")

class RetryableError(Exception):
    pass

# Logger setup
logger = structlog.get_logger()

# Service Layer
class PolicyAnalysisService:
    def __init__(self, api_base: str, timeout: float = 30.0, max_retries: int = 3):
        self.api_base = api_base.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self._client_limits = httpx.Limits(
            max_keepalive_connections=20,
            max_connections=100,
            keepalive_expiry=30.0
        )

    @asynccontextmanager
    async def get_client(self):
        """Get HTTP client with proper configuration"""
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            limits=self._client_limits,
            follow_redirects=True
        ) as client:
            yield client

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(RetryableError)
    )
    async def _make_request(
        self,
        client: httpx.AsyncClient,
        endpoint: str,
        payload: Dict[str, Any],
        phase: AnalysisPhase
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic and proper error handling"""
        url = f"{self.api_base}{endpoint}"

        try:
            response = await client.post(url, json=payload)

            # Handle different status codes appropriately
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Rate limited
                await logger.awarning("rate_limited", endpoint=endpoint)
                raise RetryableError("Rate limited")
            elif 500 <= response.status_code < 600:  # Server errors
                await logger.aerror("server_error",
                                  endpoint=endpoint,
                                  status_code=response.status_code)
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
            await logger.aerror("request_timeout", endpoint=endpoint)
            raise RetryableError("Request timeout")
        except httpx.NetworkError as e:
            await logger.aerror("network_error", endpoint=endpoint, error=str(e))
            raise RetryableError(f"Network error: {str(e)}")

    async def discover_policy(self, client: httpx.AsyncClient, website_url: str) -> Dict[str, Any]:
        """Phase 1: Policy Discovery"""
        return await self._make_request(
            client=client,
            endpoint="/policy/discover",
            payload={"website_url": website_url},
            phase=AnalysisPhase.DISCOVERY
        )

    async def extract_content(
        self,
        client: httpx.AsyncClient,
        website_url: str,
        policy_url: str
    ) -> Dict[str, Any]:
        """Phase 2: Policy Content Extraction"""
        return await self._make_request(
            client=client,
            endpoint="/policy/extract",
            payload={
                "website_url": website_url,
                "policy_url": policy_url
            },
            phase=AnalysisPhase.EXTRACTION
        )

    async def extract_features(
        self,
        client: httpx.AsyncClient,
        policy_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Phase 3: Feature Extraction"""
        # Prepare content based on language detection
        if policy_content.get("detected_language") != "en":
            payload = {
                "policy_content": policy_content["translated_content"],
                "table_content": policy_content["translated_table_content"]
            }
        else:
            payload = {
                "policy_content": policy_content["original_content"],
                "table_content": str(policy_content["table_content"])
            }

        return await self._make_request(
            client=client,
            endpoint="/cookies/extract-features",
            payload=payload,
            phase=AnalysisPhase.FEATURE_EXTRACTION
        )

    async def check_compliance(
        self,
        client: httpx.AsyncClient,
        website_url: str,
        policy_features: Dict[str, Any],
        cookies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Phase 4: Compliance Check"""
        return await self._make_request(
            client=client,
            endpoint="/violations/detect",
            payload={
                "website_url": website_url,
                "policy_json": policy_features,
                "cookies": cookies
            },
            phase=AnalysisPhase.COMPLIANCE_CHECK
        )

# Main Analysis Function
async def analyze_policy_optimized(payload: CookieSubmissionRequest) -> AnalysisResult:
    """
    Optimized policy analysis with parallel processing, proper error handling,
    and comprehensive logging.
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())
    service = PolicyAnalysisService(
        api_base=config.api_base,
        timeout=config.request_timeout,
        max_retries=config.max_retries
    )

    await logger.ainfo(
        "analysis_started",
        request_id=request_id,
        website_url=payload.website_url,
        cookies_count=len(payload.cookies)
    )

    try:
        async with service.get_client() as client:
            # Phase 1: Policy Discovery (must be first)
            await logger.ainfo("phase_started", phase="discovery", request_id=request_id)
            discovery = await service.discover_policy(client, payload.website_url)
            await logger.ainfo("phase_completed", phase="discovery", request_id=request_id)

            policy_features = {"is_specific": 0, "cookies": []}

            if discovery.get("policy_url"):
                await logger.ainfo("policy_url_found",
                                 policy_url=discovery["policy_url"],
                                 request_id=request_id)

                # Phase 2 & 3: Can be optimized with parallel execution in some cases
                # But since Phase 3 depends on Phase 2, we keep them sequential
                await logger.ainfo("phase_started", phase="extraction", request_id=request_id)

                policy_content = await service.extract_content(
                    client,
                    discovery["website_url"],
                    discovery["policy_url"]
                )
                await logger.ainfo("phase_completed", phase="extraction", request_id=request_id)

                # Phase 3: Feature Extraction
                await logger.ainfo("phase_started", phase="feature_extraction", request_id=request_id)
                policy_features = await service.extract_features(client, policy_content)
                await logger.ainfo("phase_completed", phase="feature_extraction", request_id=request_id)
            else:
                await logger.ainfo("no_policy_found",
                                 website_url=payload.website_url,
                                 request_id=request_id)

            # Phase 4: Compliance Check
            await logger.ainfo("phase_started", phase="compliance_check", request_id=request_id)
            result = await service.check_compliance(
                client,
                payload.website_url,
                policy_features,
                payload.cookies
            )
            await logger.ainfo("phase_completed", phase="compliance_check", request_id=request_id)

            # Calculate execution time
            execution_time = time.time() - start_time

            # Log comprehensive results
            await logger.ainfo(
                "analysis_completed",
                request_id=request_id,
                total_issues=result['total_issues'],
                compliance_score=result['compliance_score'],
                execution_time=execution_time,
                policy_cookies_count=result['policy_cookies_count'],
                actual_cookies_count=result['actual_cookies_count']
            )

            # Create structured result
            analysis_result = AnalysisResult(
                total_issues=result['total_issues'],
                compliance_score=result['compliance_score'],
                policy_cookies_count=result['policy_cookies_count'],
                actual_cookies_count=result['actual_cookies_count'],
                statistics=result['statistics'],
                issues=result['issues'],
                execution_time=execution_time,
                request_id=request_id
            )

            return analysis_result

    except PolicyAnalysisError as e:
        await logger.aerror(
            "analysis_failed",
            request_id=request_id,
            phase=e.phase.value,
            error=e.message,
            status_code=e.status_code,
            execution_time=time.time() - start_time
        )
        raise HTTPException(status_code=e.status_code, detail=e.message)

    except Exception as e:
        await logger.aerror(
            "analysis_unexpected_error",
            request_id=request_id,
            error=str(e),
            execution_time=time.time() - start_time
        )
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
