import uuid

from app.core.exceptions import UserNotFoundError, UserAlreadyExistsError
from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.schemas.user import UserUpdate
from app.core.security import hash_password

async def get_by_id(user_id: uuid.UUID) -> User:
    user = await User.get(user_id)
    if not user:
        raise UserNotFoundError
    return user


async def get_by_email(email: str) -> User:
    user = await User.find_one(User.email == email)
    if not user:
        raise UserNotFoundError
    return user


async def create(data: RegisterRequest) -> User:
    existing = await User.find_one(User.email == data.email)

    if existing:
        raise UserAlreadyExistsError

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
    )

    await user.insert()
    return user


async def update(user_id: uuid.UUID, data: UserUpdate) -> User:
    user = await get_by_id(user_id)

    changes = data.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(user, field, value)

    await user.save()
    return user


async def delete(user_id: uuid.UUID) -> None:
    user = await get_by_id(user_id)
    await user.delete()