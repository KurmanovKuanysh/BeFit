from pydantic import BaseModel, EmailStr, Field


class TokenData(BaseModel):
    sub: str
    email: str | None = None
    role: str | None = None
    type: str = "access"

class RefreshTokenData(BaseModel):
    sub: str
    email: str | None = None
    role: str | None = None
    type: str = "refresh"

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr = Field(min_length=8, max_length=100)
    password: str = Field(min_length=8, max_length=255)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
