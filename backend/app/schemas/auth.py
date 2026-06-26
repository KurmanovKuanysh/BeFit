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

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

class VerifyCode(BaseModel):
    email: EmailStr
    code: int = Field(
        ge=100000,
        le=999999,
        description="The verification code sent to the user's email address"
    )

class ResendCodeRequest(BaseModel):
    email: EmailStr