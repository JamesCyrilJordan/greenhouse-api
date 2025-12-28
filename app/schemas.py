from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ReadingCreate(BaseModel):
    device_id: str = Field(min_length=1, max_length=64)
    sensor: str = Field(min_length=1, max_length=64)
    value: float
    unit: Optional[str] = Field(default="", max_length=16)
    recorded_at: Optional[datetime] = None  # device can send, or server will set

class ReadingOut(BaseModel):
    id: int
    device_id: str
    sensor: str
    value: float
    unit: str
    recorded_at: datetime

    class Config:
        from_attributes = True

class PaginatedReadings(BaseModel):
    items: List[ReadingOut]
    total: int
    limit: int
    offset: int
