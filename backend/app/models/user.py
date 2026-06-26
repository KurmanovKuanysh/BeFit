from enum import Enum
from typing import Annotated

from beanie import Document, Indexed
from pydantic import EmailStr, Field
from app.models.base import TimeStampMixin, UUIDPrimaryKeyMixin

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTREMELY_ACTIVE = "extremely_active"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class Goal(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    LOSE_FAT = "lose_fat"
    MUSCLE_GAIN = "muscle_gain"
    STRENGTH_GAIN = "strength_gain"
    CALISTHENICS = "calisthenics"

class User(UUIDPrimaryKeyMixin, TimeStampMixin, Document):
    username: Annotated[
        str,
        Indexed(unique=True),
        Field(min_length=1, max_length=255),
    ]

    email: Annotated[
        EmailStr,
        Indexed(unique=True),
        Field(min_length=1, max_length=255),
    ]

    hashed_password: str

    role: UserRole = UserRole.USER

    age: Annotated[int, Field(ge=18)] | None = None
    height: Annotated[float, Field(ge=1.0)] | None = None
    current_weight: Annotated[float, Field(ge=1.0)] | None = None
    activity_level: ActivityLevel | None = None
    gender: Gender | None = None

    goal_weight: Annotated[float, Field(ge=1.0)] | None = None
    goal: Goal | None = None

    target_calories: Annotated[float, Field(ge=1)] | None = None
    target_protein: Annotated[float, Field(ge=0.0)] | None = None
    target_fat: Annotated[float, Field(ge=0.0)] | None = None
    target_carbs: Annotated[float, Field(ge=0.0)] | None = None
    target_daily_water: Annotated[float, Field(ge=0.0)] | None = None

    targets_auto_calculated: bool = False

    is_active: bool = True
    is_verified: bool = False

    class Settings:
        name = "users"