import uuid
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse

from ..models.models import (
    AnalyzeWebsiteRequest,
    SubmitCookiesRequest,
    TaskResponse,
    TaskStatusResponse,
    AnalysisReport,
    HealthCheckResponse,
    ErrorResponse,
    ViolationStatistics,
    TaskStatus,
    PolicyStatus
)
from configs.settings import get_settings, Settings

# Create router instance
router = APIRouter()

# In-memory storage for MVP (replace with Redis/MongoDB later)
task_storage: Dict[str, Dict[str, Any]] = {}
analysis_results: Dict[str, AnalysisReport] = {}


def get_current_settings() -> Settings:
    """Dependency to get current settings"""
    return get_settings()


async def analyze_website_background(task_id: str, request: AnalyzeWebsiteRequest):
    """Background task to analyze website"""
    try:
        # Update task status
        task_storage[task_id]["status"] = TaskStatus.IN_PROGRESS
        task_storage[task_id]["progress"] = 10
        task_storage[task_id]["message"] = "Starting policy discovery..."

        # Mock policy discovery (replace with actual service)
        import asyncio
        await asyncio.sleep(2)  # Simulate processing time

        task_storage[task_id]["progress"] = 30
        task_storage[task_id]["message"] = "Extracting policy content..."
        await asyncio.sleep(2)

        task_storage[task_id]["progress"] = 50
        task_storage[task_id]["message"] = "Analyzing cookie features..."
        await asyncio.sleep(2)

        task_storage[task_id]["progress"] = 70
        task_storage[task_id]["message"] = "Collecting live cookies..."
        await asyncio.sleep(1)

        task_storage[task_id]["progress"] = 90
        task_storage[task_id]["message"] = "Detecting violations..."
        await asyncio.sleep(1)

        # Create mock analysis report
        mock_report = AnalysisReport(
            task_id=task_id,
            website_url=str(request.website_url),
            policy_info={
                "policy_url": f"{request.website_url}/privacy-policy",
                "policy_status": PolicyStatus.FOUND,
                "content_length": 1500,
                "language": "en"
            },
            total_cookies_found=5,
            cookies_with_violations=2,
            total_violations=3,
            violations_by_type={
                "retention": 2,
                "third_party": 1
            },
            violations_by_category={
                "specific": 2,
                "general": 1
            },
            analysis_duration=8.0
        )

        # Store results
        analysis_results[task_id] = mock_report
        task_storage[task_id]["status"] = TaskStatus.COMPLETED
        task_storage[task_id]["progress"] = 100
        task_storage[task_id]["message"] = "Analysis completed successfully"
        task_storage[task_id]["result"] = mock_report

    except Exception as e:
        task_storage[task_id]["status"] = TaskStatus.FAILED
        task_storage[task_id]["error"] = str(e)
        task_storage[task_id]["message"] = f"Analysis failed: {str(e)}"


@router.post("/analyze", response_model=TaskResponse, summary="Start Website Analysis")
async def analyze_website(
    request: AnalyzeWebsiteRequest,
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_current_settings)
):
    """
    Start analysis of a website for cookie policy violations.

    This endpoint initiates the analysis process and returns a task ID
    that can be used to track progress and retrieve results.
    """
    try:
        # Generate unique task ID
        task_id = str(uuid.uuid4())

        # Initialize task storage
        task_storage[task_id] = {
            "task_id": task_id,
            "status": TaskStatus.PENDING,
            "progress": 0,
            "message": "Task created, waiting to start...",
            "website_url": str(request.website_url),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Add background task
        background_tasks.add_task(analyze_website_background, task_id, request)

        return TaskResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            message="Analysis task created successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create analysis task: {str(e)}"
        )


@router.get("/status/{task_id}", response_model=TaskStatusResponse, summary="Get Task Status")
async def get_task_status(task_id: str):
    """
    Get the current status of an analysis task.

    Returns detailed information about task progress, including results
    if the analysis is complete.
    """
    if task_id not in task_storage:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    task_data = task_storage[task_id]

    response = TaskStatusResponse(
        task_id=task_id,
        status=task_data["status"],
        progress=task_data.get("progress", 0),
        message=task_data["message"],
        created_at=task_data["created_at"],
        updated_at=task_data.get("updated_at", datetime.utcnow())
    )

    # Add result if completed
    if task_data["status"] == TaskStatus.COMPLETED and "result" in task_data:
        response.result = task_data["result"]

    # Add error if failed
    if task_data["status"] == TaskStatus.FAILED:
        response.error = task_data.get("error", "Unknown error")
        response.error_details = task_data.get("error_details")

    return response


@router.get("/report/{task_id}", response_model=AnalysisReport, summary="Get Analysis Report")
async def get_analysis_report(task_id: str):
    """
    Get the detailed analysis report for a completed task.

    Returns comprehensive violation information and statistics.
    """
    if task_id not in task_storage:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    task_data = task_storage[task_id]

    if task_data["status"] != TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Task {task_id} is not completed yet. Current status: {task_data['status']}"
        )

    if task_id not in analysis_results:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis results for task {task_id} not found"
        )

    return analysis_results[task_id]


@router.post("/cookies/submit", response_model=Dict[str, str], summary="Submit Live Cookies")
async def submit_live_cookies(request: SubmitCookiesRequest):
    """
    Submit live cookies collected from Chrome extension.

    This endpoint receives cookie data from the browser extension
    and associates it with an existing analysis task.
    """
    if request.task_id not in task_storage:
        raise HTTPException(
            status_code=404,
            detail=f"Task {request.task_id} not found"
        )

    # Store cookies data (in production, save to database)
    task_storage[request.task_id]["live_cookies"] = [
        cookie.dict() for cookie in request.cookies
    ]
    task_storage[request.task_id]["cookies_submitted_at"] = request.timestamp

    return {
        "status": "success",
        "message": f"Received {len(request.cookies)} cookies for task {request.task_id}"
    }


@router.get("/health", response_model=HealthCheckResponse, summary="Health Check")
async def health_check():
    """
    Health check endpoint to verify service status.

    Returns service status and dependency information.
    """
    dependencies = {
        "database": "ok",  # Mock status
        "redis": "ok",     # Mock status
        "llm_service": "ok"  # Mock status
    }

    return HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        dependencies=dependencies
    )


@router.get("/statistics", response_model=ViolationStatistics, summary="Get Violation Statistics")
async def get_violation_statistics(
    days: int = Query(default=7, description="Number of days to include in statistics")
):
    """
    Get violation statistics for dashboard.

    Returns aggregated data about violations and trends.
    """
    # Mock statistics (replace with actual database queries)
    return ViolationStatistics(
        total_analyses=len(task_storage),
        total_violations=sum(
            result.total_violations
            for result in analysis_results.values()
        ),
        most_violated_rules=[
            {"rule_id": 1, "rule_name": "Session cookie exceeds 24h", "count": 15},
            {"rule_id": 2, "rule_name": "Expiration exceeds declared", "count": 12}
        ],
        violations_by_domain={
            "example.com": 5,
            "google.com": 3,
            "facebook.com": 2
        },
        trend_data=[
            {"date": "2024-01-01", "violations": 10},
            {"date": "2024-01-02", "violations": 15}
        ]
    )


@router.delete("/tasks/{task_id}", summary="Delete Task")
async def delete_task(task_id: str):
    """
    Delete a completed or failed analysis task.

    Removes task data and associated results from storage.
    """
    if task_id not in task_storage:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    # Remove from storage
    del task_storage[task_id]
    if task_id in analysis_results:
        del analysis_results[task_id]

    return {"status": "success", "message": f"Task {task_id} deleted successfully"}


@router.get("/tasks", summary="List All Tasks")
async def list_tasks(
    status: TaskStatus = Query(None, description="Filter by task status"),
    limit: int = Query(default=50, description="Maximum number of tasks to return")
):
    """
    List analysis tasks with optional filtering.

    Returns a list of tasks with basic information.
    """
    tasks = list(task_storage.values())

    # Filter by status if provided
    if status:
        tasks = [task for task in tasks if task["status"] == status]

    # Limit results
    tasks = tasks[:limit]

    # Return simplified task info
    return [
        {
            "task_id": task["task_id"],
            "status": task["status"],
            "website_url": task["website_url"],
            "created_at": task["created_at"],
            "progress": task.get("progress", 0)
        }
        for task in tasks
    ]


# Error handlers
@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTPException",
            message=exc.detail,
            timestamp=datetime.utcnow()
        ).dict()
    )


@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            details={"exception_type": type(exc).__name__}
        ).dict()
    )
