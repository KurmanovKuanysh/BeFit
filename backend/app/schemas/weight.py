import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.weight_log import WeightLog


class WeightCreate(BaseModel):
    weight: float = Field(ge=1, le=1000)
    notes: str | None = Field(None, min_length=0, max_length=255)

class WeightUpdate(WeightCreate):
    weight: float | None = Field(None, ge=1, le=1000)
    notes: str | None = Field(None, min_length=0, max_length=255)

class WeightResponse(BaseModel):
    id: uuid.UUID
    weight: float
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WeightGraphResponse(BaseModel):
    items: list[WeightLog]
    total_points: int
    start_date: datetime
    end_date: datetime
