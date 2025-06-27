from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class CookieExtractRequest(BaseModel):
    content: str = ""

class CookieExtractResponse(BaseModel):
    generated_text: str
    model_info: str
