from fastapi import APIRouter, HTTPException, status

from app.core.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.models.token import RefreshToken
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, TokenData, RefreshTokenData, RefreshRequest, \
    LogoutRequest
from app.schemas.user import UserResponse
from app.services import user as user_service
from app.services import email as verification_service
from app.services.email import send_email, send_verification_email

router = APIRouter(prefix="/auth", tags=["Auth"])

async def create_tokens_for_user(user):
    access_token = create_access_token(
        TokenData(
            sub=str(user.id),
            email=str(user.email),
            role=user.role.value)
    )
    refresh_token_str, expires_at = create_refresh_token(
        RefreshTokenData(
            sub=str(user.id),
            email=str(user.email),
            role=user.role.value
        )
    )

    await RefreshToken(
        user=user,
        token=refresh_token_str,
        expires_at=expires_at,
    ).insert()

    return access_token, refresh_token_str

@router.post("/register", response_model=UserResponse)
async def register(
        data: RegisterRequest
):
    try:
        user = await user_service.create(data)

    except UserAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    code = await verification_service.generate_verification_code(user)
    await send_verification_email(
        email_to=user.email,
        code=code.code,
    )

    return user

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    try:
        user = await user_service.get_by_email(str(data.email))
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not verified")
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token, refresh_token = await create_tokens_for_user(user)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
        data: RefreshRequest,
):
    try:
        payload = decode_refresh_token(data.refresh_token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    token_record = await RefreshToken.find_one(
        RefreshToken.token == data.refresh_token,
        RefreshToken.is_revoked == False,
    )
    if not token_record:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked or not found")

    access_token = create_access_token(
        TokenData(
            sub=payload["sub"],
            email=payload.get("email"),
            role=payload.get("role")
        )
    )
    new_refresh_str, expires_at = create_refresh_token(
        RefreshTokenData(
            sub=payload["sub"],
            email=payload.get("email"),
            role=payload.get("role")
        )
    )

    token_record.is_revoked = True
    await token_record.save()

    await RefreshToken(
        user=token_record.user,
        token=new_refresh_str,
        expires_at=expires_at,
    ).insert()

    return TokenResponse(access_token=access_token, refresh_token=new_refresh_str)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
        data: LogoutRequest,
):
    token_record = await RefreshToken.find_one(
        RefreshToken.token == data.refresh_token,
        RefreshToken.is_revoked == False,
    )
    if token_record:
        token_record.is_revoked = True
        await token_record.save()