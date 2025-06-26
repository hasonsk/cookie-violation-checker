from fastapi import APIRouter, HTTPException

from schemas.generate import GenerateRequest, GenerateResponse
from services.cookie_extract_service import CookieExtractService
from configs.settings import settings
router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    if not CookieExtractService.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please wait for model initialization."
        )

    try:
        generated_text = await CookieExtractService.generate_text(request)

        return GenerateResponse(
            generated_text=generated_text,
            model_info=f"{settings.model_name} (Unsloth fine-tuned)"
        )

    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during generation: {str(e)}"
        )
