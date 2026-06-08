import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.services import user as user_service

http_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> User:
    try:
        token_data = decode_access_token(credentials.credentials)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await user_service.get_by_id(uuid.UUID(token_data.sub))
    return user


async def get_current_admin(
    user: User = Depends(get_current_user),
) -> User:
    if user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return user