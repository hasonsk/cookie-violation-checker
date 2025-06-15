from fastapi import HTTPException
from fastapi import FastAPI
import traceback
from fastapi.middleware.cors import CORSMiddleware

from src.routes import auth, policies, users, violations, domain_requests, websites #, reports
from src.configs.settings import settings
import uvicorn

app = FastAPI(
    title=settings.app.API_TITLE,
    description=settings.app.API_DESCRIPTION,
    version=settings.app.API_VERSION,
    debug=settings.app.APP_DEBUG
)

origins = [
    "http://localhost:3000",
    "http://192.168.0.113:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Cho phép domain frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    app.include_router(auth.router, tags=["Authentication"])
    app.include_router(users.router, prefix="/api/admin", tags=["Users"]) # Added prefix for admin users
    app.include_router(websites.router, tags=["Websites"])
    app.include_router(policies.router, tags=["Policies"])
    app.include_router(violations.router, tags=["Violations"])
    app.include_router(domain_requests.router, tags=["Domain Requests"])
    # app.include_router(reports.router, tags=["Reports"])
except Exception:
    traceback.print_exc()
    print("Lỗi khi include router")
    raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Cookie Compliance Analyzer API",
        "version": settings.app.API_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app.HOST,
        port=settings.app.PORT,
        reload=settings.app.APP_DEBUG
    )
