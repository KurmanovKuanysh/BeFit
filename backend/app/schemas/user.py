import uuid

from pydantic import BaseModel, EmailStr, ConfigDict, Field

from app.models.user import UserRole, ActivityLevel, Gender, Goal

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    age: int | None = None
    height: float | None = None
    current_weight: float | None = None
    activity_level: ActivityLevel | None = None
    gender: Gender | None = None

    goal: Goal | None = None
    goal_weight: float | None = None

class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr

    role: UserRole
    is_active: bool

    age: int | None
    height: float | None
    current_weight: float | None
    activity_level: ActivityLevel | None
    gender: Gender | None

    goal: Goal | None
    goal_weight: float | None

    target_calories: float | None
    target_protein: float | None
    target_fat: float | None
    target_carbs: float | None
    target_daily_water: float | None

    targets_auto_calculated: bool

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=2, max_length=255)
    email: EmailStr | None = None

    age: int | None = Field(None, ge=18)
    height: float | None = Field(None, ge=1.0)
    current_weight: float | None = Field(None, ge=1.0)

    activity_level: ActivityLevel | None = None
    gender: Gender | None = None

    goal: Goal | None = None
    goal_weight: float | None = Field(None, ge=1.0)

class UserAdminUpdate(BaseModel):
    role: UserRole | None = None
    is_active: bool | None = None