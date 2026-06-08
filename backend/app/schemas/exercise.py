import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.models.workout import ExerciseType, ExerciseCategory, MeasurementUnit, Level


class ExerciseCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    type: ExerciseType
    description: str | None = None
    category: list[ExerciseCategory]
    measurement_unit: MeasurementUnit
    level: Level

class ExerciseUpdate(BaseModel):
    name: str | None = None
    type: ExerciseType | None = None
    description: str | None = None
    category: list[ExerciseCategory] | None = None
    measurement_unit: MeasurementUnit | None = None
    level: Level | None = None

class FilterExercise(BaseModel):
    name: str | None = None
    type: ExerciseType | None = None
    category: ExerciseCategory | None = None
    level: Level | None = None

class ExerciseResponse(ExerciseCreate):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)

