import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pyngrok import ngrok

from configs.settings import settings
from services.cookie_extract_service import cookie_extract_service
from routes import generate



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up the application...")
    try:
        await cookie_extract_service.load_model()
        print("Model loaded successfully during startup")
    except Exception as e:
        print(f"Failed to load model during startup: {e}")

    yield

    print("Shutting down the application...")

app = FastAPI(
    title=settings.title,
    description=settings.description,
    version=settings.version,
    lifespan=lifespan
)

app.include_router(generate.router, tags=["Generation"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    public_url = ngrok.connect(8000)
    print(" * Ngrok tunnel URL:", public_url)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=settings.log_level
    )
