import uuid
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.exercise import ExerciseResponse
from app.schemas.user import UserResponse
from app.schemas.workout_plan import WorkoutPlanResponse


#=======  WORKOUT LOG ITEM  ======================================================
class WorkoutLogItemCreate(BaseModel):
    workout_log_id: uuid.UUID
    exercise_id: uuid.UUID
    sets: int = Field(gt=0)
    reps: int = Field(gt=0)
    weight: float | None = None
    duration_seconds: int | None = None

class WorkoutLogItemUpdate(BaseModel):
    sets: int | None = None
    reps: int | None = None
    weight: float | None = None
    duration_seconds: int | None = None

class WorkoutLogItemResponse(BaseModel):
    id: uuid.UUID
    exercise: ExerciseResponse
    sets: int
    reps: int
    weight: float | None = None
    duration_seconds: int | None = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

#=======  WORKOUT LOG  ======================================================

class WorkoutLogCreate(BaseModel):
    title: str
    user_id: uuid.UUID
    workout_plan_id: uuid.UUID | None = None
    duration_minutes: int | None = None
    completed: bool = False
    completed_at: datetime | None = None

class WorkoutLogUpdate(BaseModel):
    title: str | None = None
    workout_plan_id: uuid.UUID | None = None
    duration_minutes: int | None = None
    completed: bool | None = None
    completed_at: datetime | None = None

class WorkoutLogResponse(BaseModel):
    id: uuid.UUID
    title: str
    user: UserResponse
    workout_plan: WorkoutPlanResponse | None = None

    duration_minutes: int | None = None
    completed: bool = False
    completed_at: datetime | None = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WorkoutLogDetailResponse(WorkoutLogResponse):
    items: list[WorkoutLogItemResponse]