from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class GenerateRequest(BaseModel):
    prompt: str = ""
    max_length: Optional[int] = Field(512, ge=1, le=4096)
    temperature: Optional[float] = Field(0.7, ge=0.1, le=2.0)
    top_p: Optional[float] = Field(0.9, ge=0.1, le=1.0)
    top_k: Optional[int] = Field(50, ge=1, le=100)
    do_sample: Optional[bool] = Field(True)


class GenerateResponse(BaseModel):
    generated_text: str
    model_info: str
