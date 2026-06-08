import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.user import User


class WaterCreate(BaseModel):
    user_id: uuid.UUID
    amount_ml: int

class WaterUpdate(WaterCreate):
    amount_ml: int | None = None

class WaterResponse(BaseModel):
    id: uuid.UUID
    user: User
    amount_ml: int
    created_at: datetime