from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class PolicyContent(BaseModel):
    website_url: str
    policy_url: Optional[str] = None
    original_content: Optional[str] = None
    translated_content: Optional[str] = None
    table_content: Optional[List[Dict[str, Any]]] = None
    translated_table_content: Optional[str] = None
    error: Optional[str] = None
