from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class GenerateRequest(BaseModel):
    prompt: str = ""

class GenerateResponse(BaseModel):
    generated_text: str
    model_info: str
