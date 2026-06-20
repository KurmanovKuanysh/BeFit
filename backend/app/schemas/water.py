import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class WaterCreate(BaseModel):
    amount_ml: int = Field(ge=1, le=10000)

class WaterUpdate(WaterCreate):
    amount_ml: int | None = Field(None, ge=1, le=10000)

class WaterResponse(BaseModel):
    id: uuid.UUID
    amount_ml: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)