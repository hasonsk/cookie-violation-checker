from fastapi import HTTPException
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import violation_detect_router, cookie_extract_router, policy_extract_router, policy_discovery_router, auth_router
import httpx
from schemas.cookie_schema import ActualCookie, CookieSubmissionRequest
from configs.app_conf import app_config
import uvicorn
# from controllers.cookie_extract_controller import CookieExtractController
from exceptions.custom_exceptions import (
    PolicyDiscoveryError, PolicyExtractionError,
    FeatureExtractionError, ComplianceCheckError
)

# Hoặc nếu dùng Pydantic v2:
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
import os
from loguru import logger

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

load_dotenv()

API_BASE = os.getenv("API_BASE")

class Cookie(BaseModel):
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )

    name: str
    value: Optional[str] = None
    domain: str
    expirationDate: Optional[datetime] = None
    secure: bool = False
    httpOnly: bool = False
    sameSite: Optional[str] = None

# Tạo FastAPI app
app = FastAPI(
    title=app_config.api_title,
    description=app_config.api_description,
    version=app_config.api_version,
    debug=app_config.debug
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://192.168.0.113:3000", "http://127.0.0.1:3000"],  # Cho phép domain frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký routers
app.include_router(policy_discovery_router.router, tags=["policy discovery"])
app.include_router(policy_extract_router.router, tags=["policy extraction"])
app.include_router(cookie_extract_router.router, tags=["cookies extraction"])
app.include_router(violation_detect_router.router)
app.include_router(auth_router.router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Cookie Compliance Analyzer API",
        "version": app_config.api_version,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/analyze")
async def analyze_policy(payload: CookieSubmissionRequest):
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            logger.info(f"🔍 Starting policy discovery for: {payload.website_url}")

            # Add more detailed logging
            logger.info(f"API_BASE: {API_BASE}")
            discover_url = f"{API_BASE}/policy/discover"
            logger.info(f"Making request to: {discover_url}")

            resp1 = await client.post(discover_url, json={"website_url": payload.website_url})

            # Log response details
            logger.info(f"Response status: {resp1.status_code}")
            logger.info(f"Response headers: {resp1.headers}")

            # BUG FIX: Đây là lỗi chính! Bạn đang check == 200 thay vì != 200
            if resp1.status_code != 200:  # Đã sửa từ == 200 thành != 200
                logger.error(f"❌ Policy discovery failed with status {resp1.status_code}")
                try:
                    error_body = resp1.text
                    logger.error(f"Error response body: {error_body}")
                except:
                    logger.error("Could not read error response body")
                raise PolicyDiscoveryError(status_code=resp1.status_code)

            logger.info(f"✅ Policy discovery request successful")

            # Try to parse JSON response
            try:
                discovery = resp1.json()
                logger.info(f"Discovery response: {discovery}")
            except Exception as json_error:
                logger.error(f"Failed to parse JSON response: {json_error}")
                logger.error(f"Raw response text: {resp1.text}")
                raise Exception(f"Invalid JSON response from policy discovery: {json_error}")

            if discovery.get("policy_url"):
                logger.info(f"🔍 Policy URL found: {discovery['policy_url']}")

                # Phase 2: Policy Content Extraction
                extract_url = f"{API_BASE}/policy/extract"
                logger.info(f"Making request to: {extract_url}")

                resp2 = await client.post(extract_url, json={
                    "website_url": discovery["website_url"],
                    "policy_url": discovery["policy_url"]
                })

                logger.info(f"Policy extract response status: {resp2.status_code}")

                if resp2.status_code != 200:
                    logger.error(f"Policy extraction failed: {resp2.status_code}")
                    try:
                        logger.error(f"Extract error body: {resp2.text}")
                    except:
                        pass
                    raise PolicyExtractionError(status_code=resp2.status_code)

                try:
                    policy_content = resp2.json()
                    logger.info("✅ Policy content extraction completed successfully")
                except Exception as json_error:
                    logger.error(f"Failed to parse extract JSON: {json_error}")
                    raise Exception(f"Invalid JSON from policy extract: {json_error}")

                # Phase 3: Feature Extraction
                json_data = {}
                if policy_content.get("detected_language") != "en":
                    json_data = {
                        "policy_content": policy_content["translated_content"],
                        "table_content": policy_content["translated_table_content"]
                    }
                else:
                    json_data = {
                        "policy_content": policy_content["original_content"],
                        "table_content": str(policy_content["table_content"])
                    }

                features_url = f"{API_BASE}/cookies/extract-features"
                logger.info(f"Making request to: {features_url}")

                resp3 = await client.post(features_url, json=json_data)
                logger.info(f"Features extract response status: {resp3.status_code}")

                if resp3.status_code != 200:
                    logger.error(f"Feature extraction failed: {resp3.status_code}")
                    try:
                        logger.error(f"Features error body: {resp3.text}")
                    except:
                        pass
                    raise FeatureExtractionError(status_code=resp3.status_code)

                try:
                    features = resp3.json()
                    logger.info(f"✅ Feature extraction completed successfully")
                except Exception as json_error:
                    logger.error(f"Failed to parse features JSON: {json_error}")
                    raise Exception(f"Invalid JSON from features extract: {json_error}")
            else:
                logger.info("No policy URL found, using default features")
                features = {"is_specific": 0, "cookies": []}

            logger.info(f"🍪 Received cookies: {len(payload.cookies)}")

            # Phase 4: Compliance Check
            violations_url = f"{API_BASE}/violations/detect"
            logger.info(f"Making request to: {violations_url}")

            resp4 = await client.post(violations_url, json={
                "website_url": payload.website_url,
                "policy_json": features,
                "cookies": payload.cookies,
            })

            logger.info(f"Violations detect response status: {resp4.status_code}")

            if resp4.status_code != 200:
                logger.error(f"Compliance check failed: {resp4.status_code}")
                try:
                    logger.error(f"Violations error body: {resp4.text}")
                except:
                    pass
                raise ComplianceCheckError(status_code=resp4.status_code)

            try:
                result = resp4.json()
            except Exception as json_error:
                logger.error(f"Failed to parse violations JSON: {json_error}")
                raise Exception(f"Invalid JSON from violations detect: {json_error}")

            logger.info("+++++++++++++++++++++DONE++++++++++++++++++++++")
            logger.info("=== COOKIE POLICY COMPLIANCE ANALYSIS ===")
            print(f"Total Issues Found: {result['total_issues']}")
            print(f"Compliance Score: {result['compliance_score']}/100")
            print(f"Policy Cookies: {result['policy_cookies_count']}")
            print(f"Actual Cookies: {result['actual_cookies_count']}")

            print("\n=== ISSUES BY SEVERITY ===")
            for severity, count in result['statistics']['by_severity'].items():
                print(f"{severity}: {count}")

            logger.info("The declared cookies: ", result)
            return result

        except PolicyDiscoveryError as e:
            logger.error(f"Policy discovery error: {e}")
            raise HTTPException(status_code=500, detail=f"Policy discovery failed: {str(e)}")
        except PolicyExtractionError as e:
            logger.error(f"Policy extraction error: {e}")
            raise HTTPException(status_code=500, detail=f"Policy extraction failed: {str(e)}")
        except FeatureExtractionError as e:
            logger.error(f"Feature extraction error: {e}")
            raise HTTPException(status_code=500, detail=f"Feature extraction failed: {str(e)}")
        except ComplianceCheckError as e:
            logger.error(f"Compliance check error: {e}")
            raise HTTPException(status_code=500, detail=f"Compliance check failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=app_config.host,
        port=app_config.port,
        reload=app_config.debug
    )
