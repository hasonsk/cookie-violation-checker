from fastapi import APIRouter, HTTPException, status

from schemas.generate import GenerateRequest, GenerateResponse
from services.cookie_extract_service import cookie_extract_service
from configs.settings import settings
from exceptions.custom_exceptions import ModelNotLoadedException, LLMServiceException

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    if not cookie_extract_service.is_loaded:
        raise ModelNotLoadedException()

    try:
        generated_text = await cookie_extract_service.generate_text(request)

        return GenerateResponse(
            generated_text=generated_text,
            model_info=settings.model_name
        )

    except RuntimeError as e:
        raise LLMServiceException(detail=f"Generation failed: {str(e)}")
    except Exception as e:
        raise LLMServiceException(detail=f"Unexpected error during generation: {str(e)}")
