import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.user import User
from app.schemas.user import UserResponse


class WeightCreate(BaseModel):
    user_id: uuid.UUID
    weight: float
    notes: str | None = None

class WeightUpdate(WeightCreate):
    weight: float | None = None
    notes: str | None = None

class WeightResponse(BaseModel):
    id: uuid.UUID
    user: UserResponse
    weight: float
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)