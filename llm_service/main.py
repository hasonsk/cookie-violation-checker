import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pyngrok import ngrok

from configs.settings import settings
from schemas.extract import CookieExtractRequest
from services.cookie_extract_service import LlamaCookieExtractionService

app = FastAPI(
    title=settings.title,
    description=settings.description,
    version=settings.version,
)

cookie_extractor = LlamaCookieExtractionService(
    model_path="sonhask/meta-Llama-3.1-8B-Instruct-bnb-4bit-DATN"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract")
def extract_cookie_info(request: CookieExtractRequest):
    response = cookie_extractor.generate_response(request.content)
    return {"result": response}

if __name__ == "__main__":
    public_url = ngrok.connect(8000)
    print(" * Ngrok tunnel URL:", public_url)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=settings.log_level
    )
