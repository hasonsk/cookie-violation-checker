import logging
import sys
from typing import Optional
from models.models import AnalyzeWebsiteRequest, ErrorResponse, HealthCheckResponse, LiveCookieData, SubmitCookiesRequest, TaskResponse
from config.settings import Settings, get_settings, validate_environment
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
from celery import Celery
from datetime import datetime, timedelta
from uuid import uuid4

# Import local modules (these would be in separate files)
# from api.routes import router as api_router
# from api.middleware import RateLimitMiddleware, RequestLoggingMiddleware
# from database.connection import get_database, get_redis_connection
# from services.policy_finder import PolicyFinderService
# from services.content_extractor import ContentExtractorService
# from services.feature_analyzer import FeatureAnalyzerService
# from services.cookie_collector import CookieCollectorService
# from services.violation_detector import ViolationDetectorService
# from services.report_generator import ReportGeneratorService

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logging.info("Starting Cookie Violations Check API...")

    # Validate environment
    # try:
    #     validate_environment()
    #     logging.info("Environment validation passed")
    # except ValueError as e:
    #     logging.error(f"Environment validation failed: {e}")
    #     sys.exit(1)

    # Initialize database connections
    settings = get_settings()

    # MongoDB connection
    try:
        app.state.mongodb_client = AsyncIOMotorClient(settings.mongodb_url)
        app.state.database = app.state.mongodb_client[settings.mongodb_database]
        # Test connection
        await app.state.mongodb_client.admin.command('ping')
        logging.info("MongoDB connection established")
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)

    # Redis connection
    try:
        app.state.redis = redis.from_url(
            settings.redis_url,
            db=settings.redis_db,
            decode_responses=True
        )
        # Test connection
        await app.state.redis.ping()
        logging.info("Redis connection established")
    except Exception as e:
        logging.error(f"Failed to connect to Redis: {e}")
        sys.exit(1)

    # Initialize Celery app
    app.state.celery_app = Celery(
        'cookie_violations',
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend
    )

    # Configure Celery
    app.state.celery_app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=settings.task_timeout,
        task_soft_time_limit=settings.task_timeout - 30,
        worker_max_tasks_per_child=100,
    )

    logging.info("Application startup completed")

    yield

    # Shutdown
    logging.info("Shutting down Cookie Violations Check API...")

    # Close database connections
    if hasattr(app.state, 'mongodb_client'):
        app.state.mongodb_client.close()
        logging.info("MongoDB connection closed")

    if hasattr(app.state, 'redis'):
        await app.state.redis.close()
        logging.info("Redis connection closed")

    logging.info("Application shutdown completed")

# ==============================================================================
# FASTAPI APPLICATION SETUP
# ==============================================================================

def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=settings.log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log') if not settings.debug else logging.NullHandler()
        ]
    )

    # Create FastAPI app
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.api_version,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # Add middleware
    setup_middleware(app, settings)

    # Add routes
    setup_routes(app)

    # Add exception handlers
    setup_exception_handlers(app)

    return app

def setup_middleware(app: FastAPI, settings: Settings):
    """Setup application middleware."""

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Trusted host middleware (in production)
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure based on your deployment
        )

    # Custom middleware for request logging and rate limiting would go here
    # app.add_middleware(RequestLoggingMiddleware)
    # app.add_middleware(RateLimitMiddleware)

def setup_exception_handlers(app: FastAPI):
    """Setup custom exception handlers."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                error="Validation Error",
                message=str(exc),
                request_id=getattr(request.state, 'request_id', None)
            ).dict()
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=f"HTTP {exc.status_code}",
                message=exc.detail,
                request_id=getattr(request.state, 'request_id', None)
            ).dict()
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logging.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="Internal Server Error",
                message="An unexpected error occurred",
                request_id=getattr(request.state, 'request_id', None)
            ).dict()
        )

def setup_routes(app: FastAPI):
    """Setup application routes."""

    @app.get("/health", response_model=HealthCheckResponse)
    async def health_check():
        """Health check endpoint."""
        settings = get_settings()
        dependencies = {}

        # Check MongoDB
        try:
            await app.state.database.command('ping')
            dependencies["mongodb"] = "healthy"
        except Exception:
            dependencies["mongodb"] = "unhealthy"

        # Check Redis
        try:
            await app.state.redis.ping()
            dependencies["redis"] = "healthy"
        except Exception:
            dependencies["redis"] = "unhealthy"

        # Check if all dependencies are healthy
        overall_status = "healthy" if all(
            status == "healthy" for status in dependencies.values()
        ) else "unhealthy"

        return HealthCheckResponse(
            status=overall_status,
            version=settings.api_version,
            dependencies=dependencies
        )

    @app.post("/analyze", response_model=TaskResponse)
    async def analyze_website(request: AnalyzeWebsiteRequest):
        """Start website analysis."""
        task_id = str(uuid4())

        # Store task in database
        task_data = {
            "task_id": task_id,
            "website_url": request.website_url,
            "status": "PENDING",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "progress": 0
        }

        await app.state.database.tasks.insert_one(task_data)

        # Queue analysis task with Celery
        # app.state.celery_app.send_task(
        #     'analyze_website_task',
        #     args=[task_id, request.website_url],
        #     task_id=task_id
        # )

        return TaskResponse(
            task_id=task_id,
            message=f"Analysis started for {request.website_url}"
        )

    @app.get("/status/{task_id}")
    async def get_task_status(task_id: str):
        """Get task status."""
        task = await app.state.database.tasks.find_one({"task_id": task_id})

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        return {
            "task_id": task_id,
            "status": task.get("status", "UNKNOWN"),
            "progress": task.get("progress", 0),
            "message": task.get("message", ""),
            "created_at": task.get("created_at"),
            "updated_at": task.get("updated_at"),
            "result": task.get("result"),
            "error": task.get("error"),
            "error_details": task.get("error_details")
        }

    @app.get("/report/{task_id}")
    async def get_analysis_report(task_id: str):
        """Get analysis report."""
        task = await app.state.database.tasks.find_one({"task_id": task_id})

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        if task.get("status") != "COMPLETED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task not completed yet"
            )

        return task.get("result", {})

    @app.post("/cookies/submit")
    async def submit_cookies(request: SubmitCookiesRequest):
        """Submit cookies from browser extension."""
        # Verify task exists
        task = await app.state.database.tasks.find_one({"task_id": request.task_id})

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Store cookies data
        cookie_data = {
            "task_id": request.task_id,
            "cookies": [cookie.dict() for cookie in request.cookies],
            "timestamp": request.timestamp,
            "created_at": datetime.utcnow()
        }

        await app.state.database.cookies.insert_one(cookie_data)

        # Update task status
        await app.state.database.tasks.update_one(
            {"task_id": request.task_id},
            {
                "$set": {
                    "updated_at": datetime.utcnow(),
                    "message": "Cookies received from browser extension"
                }
            }
        )

        return {
            "status": "success",
            "message": f"Received {len(request.cookies)} cookies for task {request.task_id}"
        }

    @app.get("/statistics")
    async def get_violation_statistics(days: int = 7):
        """Get violation statistics."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # This would be implemented with proper aggregation queries
        # For now, returning mock data structure
        return {
            "total_analyses": 0,
            "total_violations": 0,
            "most_violated_rules": [],
            "violations_by_domain": {},
            "trend_data": []
        }

    @app.delete("/tasks/{task_id}")
    async def delete_task(task_id: str):
        """Delete a task and its associated data."""
        result = await app.state.database.tasks.delete_one({"task_id": task_id})

        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Also delete associated cookies and reports
        await app.state.database.cookies.delete_many({"task_id": task_id})
        await app.state.database.reports.delete_many({"task_id": task_id})

        return {
            "status": "success",
            "message": f"Task {task_id} and associated data deleted"
        }

    @app.get("/tasks")
    async def list_tasks(status: Optional[str] = None, limit: int = 50):
        """List all tasks with optional filtering."""
        query = {}
        if status:
            query["status"] = status

        cursor = app.state.database.tasks.find(query).limit(limit).sort("created_at", -1)
        tasks = []

        async for task in cursor:
            tasks.append({
                "task_id": task["task_id"],
                "status": task["status"],
                "website_url": task["website_url"],
                "created_at": task["created_at"],
                "progress": task.get("progress", 0)
            })

        return tasks

# ==============================================================================
# APPLICATION INSTANCE
# ==============================================================================

# Create the FastAPI application instance
app = create_application()

# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    settings = get_settings()

    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers if not settings.debug else 1,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )
