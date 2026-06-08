from datetime import datetime, UTC
from uuid import UUID

from app.core.exceptions import UserAlreadyExistsError, UnauthorizedError, InvalidTokenError
from app.core.security import create_access_token, create_refresh_token, verify_password, decode_refresh_token, hash_password
from app.models.token import RefreshToken
from app.models.user import User
from app.schemas.auth import RegisterRequest, TokenData, RefreshTokenData


async def register(
        data: RegisterRequest
) -> tuple[User, str, str]:
    existing = await User.find_one(User.email == data.email)
    if existing is not None:
        raise UserAlreadyExistsError

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    await user.insert()
    access, refresh_str = await _issue_tokens(user)
    return user, access, refresh_str

async def login(
        email: str,
        password: str
) -> tuple[User, str, str]:
    user = await User.find_one(User.email == email)
    if user is None or not user.is_active:
        raise UnauthorizedError

    if not verify_password(password, user.hashed_password):
        raise UnauthorizedError

    access, refresh_str = await _issue_tokens(user)
    return user, access, refresh_str

async def refresh(
    refresh_token: str | None
) -> tuple[str,str]:
    if not refresh_token:
        raise InvalidTokenError

    try:
        payload = decode_refresh_token(refresh_token)
    except Exception:
        raise InvalidTokenError

    user_id = UUID(payload["sub"])

    stored = await RefreshToken.find_one(RefreshToken.token == refresh_token)
    if stored is None or stored.is_revoked:
        raise InvalidTokenError
    if stored.expires_at < datetime.now(UTC):
        raise InvalidTokenError

    stored.is_revoked = True
    await stored.save()

    user = await User.get(user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError

    access, refresh_str = await _issue_tokens(user)
    return access, refresh_str


async def _issue_tokens(user: User) -> tuple[str, str]:
    access = create_access_token(
        TokenData(
            sub=str(user.id),
            email=str(user.email),
            role=user.role.value
        )
    )
    refresh_str, expires_at = create_refresh_token(
        RefreshTokenData(sub=str(user.id))
    )

    await RefreshToken(
        user=user,  # type: ignore[arg-type]
        token=refresh_str,
        expires_at=expires_at,
    ).insert()

    return access, refresh_str