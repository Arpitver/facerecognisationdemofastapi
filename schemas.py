from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PersonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    image_path: Optional[str] = None
    created_at: datetime


class RecognizeResult(BaseModel):
    matched: bool
    person_id: Optional[int] = None
    name: Optional[str] = None
    distance: Optional[float] = None 
    confidence: Optional[float] = None  # 0-100
