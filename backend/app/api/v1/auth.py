from fastapi import APIRouter, HTTPException, status

from app.core.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.models.token import RefreshToken
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, TokenData, RefreshTokenData
from app.services import user as user_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse)
async def register(
        data: RegisterRequest
):
    try:
        user = await user_service.create(data)
    except UserAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    access_token = create_access_token(
        TokenData(
            sub=str(user.id),
            email=str(user.email),
            role=user.role.value)
    )
    refresh_token_str, expires_at = create_refresh_token(
        RefreshTokenData(sub=str(user.id), email=str(user.email), role=user.role.value)
    )

    await RefreshToken(
        user=user,  # type: ignore[arg-type]
        token=refresh_token_str,
        expires_at=expires_at,
    ).insert()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token_str)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    try:
        user = await user_service.get_by_email(str(data.email))
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(
        TokenData(
            sub=str(user.id),
            email=str(user.email),
            role=user.role.value)
    )
    refresh_token_str, expires_at = create_refresh_token(
        RefreshTokenData(sub=str(user.id), email=str(user.email), role=user.role.value)
    )

    await RefreshToken(
        user=user,  # type: ignore[arg-type]
        token=refresh_token_str,
        expires_at=expires_at,
    ).insert()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token_str)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_token: str):
    try:
        payload = decode_refresh_token(refresh_token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    token_record = await RefreshToken.find_one(
        RefreshToken.token == refresh_token,
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
async def logout(refresh_token: str):
    token_record = await RefreshToken.find_one(
        RefreshToken.token == refresh_token,
        RefreshToken.is_revoked == False,
    )
    if not token_record:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not found or already revoked")

    token_record.is_revoked = True
    await token_record.save()