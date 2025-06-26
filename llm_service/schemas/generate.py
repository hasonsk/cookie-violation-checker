from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class GenerateRequest(BaseModel):
    prompt: str = ""
    max_length: Optional[int] = Field(2048, ge=1, le=2048)
    temperature: Optional[float] = Field(0.0)
    top_p: Optional[float] = Field(1.0)
    do_sample: Optional[bool] = Field(False)

class GenerateResponse(BaseModel):
    generated_text: str
    model_info: str
