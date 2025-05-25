from fastapi import FastAPI
from routers import violation_detect_router, cookie_extract_router, policy_extract_router, policy_discovery_router
from configs.app_conf import app_config
# from controllers.cookie_extract_controller import CookieExtractController

# Tạo FastAPI app
app = FastAPI(
    title=app_config.api_title,
    description=app_config.api_description,
    version=app_config.api_version,
    debug=app_config.debug
)

# Đăng ký routers
# app.include_router(violation_detect_router.router)
# app.include_router(cookie_extract_router.router, tags=["cookies extraction"])
# app.include_router(policy_extract_router.router, tags=["policy extraction"])
app.include_router(policy_discovery_router.router, tags=["policy discovery"])

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=app_config.host,
        port=app_config.port,
        reload=app_config.debug
    )
