from pydantic import Field, HttpUrl
from typing import Optional, List
from enum import Enum

from src.models.base import BaseMongoDBModel, PyObjectId

class Website(BaseMongoDBModel):
    domain: HttpUrl = Field(..., description="The URL of the website")
    policy_url: Optional[HttpUrl] = Field(default=None, description="The URL of the cookie policy page")
    provider_id: PyObjectId = Field(..., description="ID of the provider associated with this website")
    last_scanned_at: Optional[str] = Field(default=None, description="Timestamp of the last scan")
    status: Optional[str] = Field(default="pending", description="Current status of the website (e.g., pending, active, error)")
    notes: Optional[str] = Field(default=None, description="Any additional notes about the website")
