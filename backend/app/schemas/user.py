import uuid

from pydantic import BaseModel, EmailStr, ConfigDict

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

class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    age: int | None = None
    height: float | None = None
    current_weight: float | None = None
    activity_level: ActivityLevel | None = None
    gender: Gender | None = None

    target_calories: float | None = None
    target_protein: float | None = None
    target_fat: float | None = None
    target_carbs: float | None = None
    target_daily_water: float | None = None

    model_config = ConfigDict(from_attributes=True)

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    role: UserRole | None = None
