from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CalendarSchema(BaseModel):
    """Schema for a calendar."""
    id: str
    name: str
    description: Optional[str] = None
    url: str


class EventSchema(BaseModel):
    """Schema for a calendar event."""
    id: str
    summary: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None 