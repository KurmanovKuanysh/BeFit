from datetime import datetime, timezone, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import PasswordVerifyError
from app.schemas.auth import TokenData, RefreshTokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        raise PasswordVerifyError from e

def create_access_token(data: TokenData, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)))
    to_encode = {"sub": data.sub, "email": data.email, "role": data.role, "type": data.type, "exp": expire,}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return TokenData(**payload)
    except JWTError:
        raise

def create_refresh_token(data: RefreshTokenData) -> tuple[str, datetime]:
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(settings.REFRESH_TOKEN_EXPIRE_MINUTES))

    payload = {"sub": data.sub, "email": data.email, "role": data.role, "type": data.type, "exp": expire,}

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, expire

def decode_refresh_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, [settings.ALGORITHM])
    except JWTError:
        raise