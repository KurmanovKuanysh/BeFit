import uuid

from app.core.exceptions import UserNotFoundError, UserAlreadyExistsError
from app.models.user import User, UserRole
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

async def list_users(
    page: int = 1,
    page_size: int = 10,
    role: UserRole | None = None,
    is_active: bool | None = None,
) -> tuple[list[User], int]:
    skip = (page - 1) * page_size

    filters: dict = {}

    if role is not None:
        filters["role"] = role
    if is_active is not None:
        filters["is_active"] = is_active
    query = User.find(filters)

    total = await query.count()
    items = await query.skip(skip).limit(page_size).sort("-created_at").to_list()

    return items, total

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


async def update(
        user_id: uuid.UUID,
        data: UserUpdate
) -> User:
    user = await get_by_id(user_id)

    changes = data.model_dump(exclude_unset=True)

    if 'password' in changes:
        user.hashed_password = hash_password(changes.pop('password'))
    if 'email' in changes and changes['email'] != user.email:
        existing = await User.find_one(User.email == changes['email'])
        if existing:
            raise UserAlreadyExistsError

    for field, value in changes.items():
        setattr(user, field, value)

    await user.save()
    return user


async def delete(user_id: uuid.UUID) -> None:
    user = await get_by_id(user_id)
    await user.delete()