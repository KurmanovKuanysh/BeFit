import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.workout import Level
from app.schemas.exercise import ExerciseResponse
from app.schemas.user import UserResponse


#=======  WORKOUT PLAN ITEM ======================================================

class WorkoutPlanItemCreate(BaseModel):
    exercise_id: uuid.UUID
    sets: int
    reps: int
    weight: float | None = None
    duration_seconds: int | None = None

class WorkoutPlanItemUpdate(BaseModel):
    sets: int | None = None
    reps: int | None = None
    weight: float | None = None
    duration_seconds: int | None = None

class WorkoutPlanItemResponse(BaseModel):
    id: uuid.UUID
    exercise: ExerciseResponse
    sets: int
    reps: int
    weight: float | None = None
    duration_seconds: int | None = None

    model_config = ConfigDict(from_attributes=True)

#=======  WORKOUT PLAN  ======================================================

class WorkoutPlanCreate(BaseModel):
    title: str
    level: Level
    private: bool = False



class WorkoutPlanUpdate(BaseModel):
    title: str | None = None
    level: Level | None = None
    private: bool | None = None

class WorkoutPlanResponse(BaseModel):
    id: uuid.UUID
    title: str
    level: Level
    created_by: UserResponse | None = None
    private: bool = False

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WorkoutPlanDetailResponse(WorkoutPlanResponse):
    items: list[WorkoutPlanItemResponse]
