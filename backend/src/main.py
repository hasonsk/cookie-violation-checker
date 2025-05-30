from fastapi import HTTPException
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import violation_detect_router, cookie_extract_router, policy_extract_router, policy_discovery_router, auth_router
import httpx
from schemas.cookie_schema import ActualCookie, CookieSubmissionRequest
from configs.app_conf import app_config
import uvicorn
# from controllers.cookie_extract_controller import CookieExtractController

# Hoặc nếu dùng Pydantic v2:
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

API_BASE = os.getenv("API_BASE")

class Cookie(BaseModel):
    """Cookie schema với JSON serialization config cho Pydantic v2"""
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
    allow_origins=["http://localhost:3000"],  # Cho phép domain frontend
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
    async with httpx.AsyncClient() as client:
        try:
            # Phase 1: Policy Discovery
            print("🔍 Starting policy discovery for:", payload.website_url)
            resp1 = await client.post(f"{API_BASE}/policy/discover", json={"website_url": payload.website_url})
            if resp1.status_code != 200:
                raise HTTPException(status_code=resp1.status_code, detail="Policy Discovery failed")
            discovery = resp1.json()
            print("✅ Policy discovery completed successfully", discovery)

            if discovery.get("policy_url"):
                print("🔍 Policy URL found:", discovery["policy_url"])
                # Phase 2: Policy Content Extraction
                resp2 = await client.post(f"{API_BASE}/policy/extract", json={
                    "website_url": discovery["website_url"],
                    "policy_url": discovery["policy_url"]
                })
                if resp2.status_code != 200:
                    raise HTTPException(status_code=resp2.status_code, detail="Policy Extraction failed")
                policy_content = resp2.json()
                print("✅ Policy content extraction completed successfully", policy_content)

                # Phase 3: Feature Extraction
                json = {}
                if policy_content.get("detected_language") != "en":
                    json = {
                    "policy_content": policy_content["translated_content"],
                    "table_content": policy_content["translated_table_content"]
                    }
                else:
                    json = {
                    "policy_content": policy_content["original_content"],
                    "table_content": str(policy_content["table_content"])
                    }
                resp3 = await client.post(f"{API_BASE}/cookies/extract-features", json=json)
                if resp3.status_code != 200:
                    raise HTTPException(status_code=resp3.status_code, detail="Feature Extraction failed")
                features = resp3.json()
                print("✅ Feature extraction completed successfully", features)
            else:
                features = {"is_specific": 0, "cookies": []}

            # print("🔍 Starting cookie extraction for:", payload.website_url)
            print("🍪 Received cookies:", len(payload.cookies))
            # Phase 4: Compliance Check
            resp4 = await client.post(f"{API_BASE}/violations/detect", json={
                "website_url": payload.website_url,
                "policy_json": features,
                "cookies":  payload.cookies,
            })
            if resp4.status_code != 200:
                raise HTTPException(status_code=resp4.status_code, detail="Compliance Checking failed")
            result = resp4.json()
            print("+++++++++++++++++++++DONE++++++++++++++++++++++")
            print("=== COOKIE POLICY COMPLIANCE ANALYSIS ===")
            print(f"Total Issues Found: {result['total_issues']}")
            print(f"Compliance Score: {result['compliance_score']}/100")
            print(f"Policy Cookies: {result['policy_cookies_count']}")
            print(f"Actual Cookies: {result['actual_cookies_count']}")

            print("\n=== ISSUES BY SEVERITY ===")
            for severity, count in result['statistics']['by_severity'].items():
                print(f"{severity}: {count}")

            print("\n=== DETAILED ISSUES ===")
            for issue in result['issues']:
                print(f"[{issue['severity']}] Issue #{issue['issue_id']} - {issue['category']}/{issue['type']}")
                print(f"Cookie: {issue['cookie_name']}")
                print(f"Description: {issue['description']}")
                print(f"Details: {issue['details']}")
                print("-" * 50)
            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=app_config.host,
        port=app_config.port,
        reload=app_config.debug
    )
