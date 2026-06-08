from datetime import datetime
from enum import Enum

from beanie import Document, Link, before_event, Delete, Indexed
from pydantic import PositiveInt

from app.models.base import TimeStampMixin, UUIDPrimaryKeyMixin
from typing import List, Annotated
from app.models.user import User

class Level(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class MeasurementUnit(str, Enum):
    KG = "kg"
    REPS = "reps"
    SECONDS = "seconds"

class ExerciseType(str, Enum):
    CARDIO = "cardio"
    STRENGTH = "strength"
    ENDURANCE = "endurance"

class ExerciseCategory(str, Enum):
    AEROBICS = "aerobics"
    ANAEROBICS = "anaerobics"
    CORE = "core"
    LEG = "leg"
    SHOULDER = "shoulder"
    BACK = "back"
    BICEPS = "biceps"
    TRICEPS = "triceps"
    CHEST = "chest"
    QUADS = "quads"

#========= MODELS  ==========================================================================

class Exercise(UUIDPrimaryKeyMixin, TimeStampMixin,Document):
    name: Annotated[str, Indexed(unique=True)]
    type: ExerciseType
    description: str | None = None
    category: List[ExerciseCategory]
    measurement_unit: MeasurementUnit
    level: Level

    @before_event(Delete)
    async def cascade_delete(self):
       await WorkoutPlanItem.find({"exercise.$id": self.id}).delete()
       await WorkoutLogItem.find({"exercise.$id": self.id}).delete()

    class Settings:
        name = "exercises"
        indexes = [
            "category",
            "type",
            "level"
        ]

class WorkoutPlan(UUIDPrimaryKeyMixin, TimeStampMixin,Document):
    title: str
    level: Level
    created_by: Link[User] | None = None

    @before_event(Delete)
    async def cascade_delete(self):
        await WorkoutPlanItem.find({"workout_plan.$id": self.id}).delete()

    class Settings:
        name = "workout_plans"
        indexes = [
            "created_by"
        ]

class WorkoutPlanItem(UUIDPrimaryKeyMixin, TimeStampMixin,Document):
    workout_plan: Link[WorkoutPlan]
    exercise: Link[Exercise]
    sets: PositiveInt
    reps: PositiveInt
    weight: float | None = None
    duration_seconds: int | None = None

    class Settings:
        name = "workout_plan_items"
        indexes = [
            "workout_plan",
            "exercise",
            [("workout_plan", 1), ("exercise", 1)],

        ]

class WorkoutLog(UUIDPrimaryKeyMixin, TimeStampMixin,Document):
    title: str
    user: Link[User]
    workout_plan: Link[WorkoutPlan] | None = None
    duration_minutes: int | None = None
    completed: bool = False
    completed_at: datetime | None = None

    @before_event(Delete)
    async def cascade_delete(self):
        await WorkoutLogItem.find({"workout_log.$id": self.id}).delete()

    class Settings:
        name = "workout_logs"
        indexes = [
            "user",
            "workout_plan",
            "completed",
        ]


class WorkoutLogItem(UUIDPrimaryKeyMixin, TimeStampMixin,Document):
    workout_log: Link[WorkoutLog]
    exercise: Link[Exercise]
    sets: PositiveInt
    reps: PositiveInt
    weight: float | None = None
    duration_seconds: int | None = None

    class Settings:
        name = "workout_log_items"
        indexes = [
            "workout_log",
            "exercise"
        ]


