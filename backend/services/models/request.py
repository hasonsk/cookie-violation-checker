from pydantic import BaseModel

class WebsiteRequest(BaseModel):
    url: str
    force_refresh: bool = False
    scan_duration: int = 300  # Mặc định 5 phút
