from fastapi import HTTPException
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers import violation_detect_router, cookie_extract_router, policy_extract_router, policy_discovery_router, auth_router, analyze_router
from src.configs.settings import settings
import uvicorn

# Tạo FastAPI app
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

app.include_router(policy_discovery_router.router, tags=["policy discovery"])
app.include_router(policy_extract_router.router, tags=["policy extraction"])
app.include_router(cookie_extract_router.router, tags=["cookies extraction"])
app.include_router(violation_detect_router.router)
app.include_router(auth_router.router)
app.include_router(analyze_router.router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Cookie Compliance Analyzer API",
        "version": API_VERSION,
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
