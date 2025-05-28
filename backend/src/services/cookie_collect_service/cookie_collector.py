from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
from src.services.violation_detect_service.violation_detector import ViolationAnalyzer  # Replace 'some_module' with the actual module name

class ActualCookie(BaseModel):
    """Cấu trúc cookie thu thập được thực tế"""
    name: str
    value: str
    domain: str
    expires: Optional[datetime]
    secure: bool
    httpOnly: bool
    sameSite: Optional[str]
    thirdParties: Optional[List[str]]

app = FastAPI()

# Định nghĩa cấu trúc cookie (giống object từ chrome.cookies.getAll)
class Cookie(BaseModel):
    name: str
    value: Optional[str] = None
    domain: str
    path: str
    secure: bool
    httpOnly: bool
    sameSite: Optional[str] = None
    expirationDate: Optional[datetime] = None

@app.post("/submit-cookies")
async def receive_cookies(cookies: List[Cookie]):
# async def receive_cookies(request: Request):
#     body = await request.json()
#     print("Received raw data:", body)  # In ra dữ liệu nhận được
#     return {"message": "Received"}
    print("\n🍪 Received cookies:", len(cookies))
    policy_json = """{
        "is_specific": 1,
        "cookies": [
            {
                "cookie_name": "_ga",
                "declared_purpose": "Analytical",
                "declared_retention": "13 months",
                "declared_third_parties": ["Google Analytics"],
                "declared_description": "This Google Analytics cookie tracks user sessions and behavior."
            },
            {
                "cookie_name": "session_id",
                "declared_purpose": "Strictly Necessary",
                "declared_retention": "Session",
                "declared_third_parties": ["First Party"],
                "declared_description": "Essential cookie for maintaining user login sessions."
            },
            {
                "cookie_name": "check_rule_5",
                "declared_purpose": "Strictly Necessary",
                "declared_retention": "short-term",
                "declared_third_parties": ["First Party"],
                "declared_description": "Essential cookie for maintaining user login sessions."
            }
        ]
    }"""

    actual_cookies = [
        ActualCookie(
            name=c.name,
            value=c.value,
            domain=c.domain,
            expires=c.expirationDate.replace(tzinfo=None) if c.expirationDate else None,
            secure=c.secure,
            httpOnly=c.httpOnly,
            sameSite=c.sameSite,
            thirdParties=[]  # Placeholder for third-party requests
        )
        for c in cookies
    ]

    analyzer = ViolationAnalyzer()
    result = analyzer.analyze_compliance(policy_json, actual_cookies, "example.com")

    print("=== COOKIE POLICY COMPLIANCE ANALYSIS ===")
    print(f"Total Issues Found: {result['total_issues']}")
    print(f"Compliance Score: {result['compliance_score']}/100")
    print(f"Policy Cookies: {result['policy_cookies_count']}")
    print(f"Actual Cookies: {result['actual_cookies_count']}")

    print("\n=== ISSUES BY SEVERITY ===")
    for severity, count in result['statistics']['by_severity'].items():
        print(f"{severity}: {count}")

    # print("\n=== DETAILED ISSUES ===")
    # for issue in result['issues']:
    #     print(f"[{issue['severity']}] Issue #{issue['issue_id']} - {issue['category']}/{issue['type']}")
    #     print(f"Cookie: {issue['cookie_name']}")
    #     print(f"Description: {issue['description']}")
    #     print(f"Details: {issue['details']}")
    #     print("-" * 50)

    return {"status": "received", "count": len(cookies), "violation": result}




# uvicorn get_cookies:app --reload --port 8000
