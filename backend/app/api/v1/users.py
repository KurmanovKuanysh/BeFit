import uuid

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_admin
from app.schemas.auth import RegisterRequest
from app.schemas.user import UserResponse, UserUpdate
from app.services import user as user_service
from app.schemas.common import Paginated

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=Paginated[UserResponse])
async def list_users(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        role: str | None = None,
        is_active: bool | None = None,
        _: UserResponse = Depends(get_current_admin)
):
    items, total = await user_service.list_users(page, page_size, role, is_active)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total else 0
    }


@router.post("", response_model=UserResponse)
async def create_user(
        data: RegisterRequest,
        _: UserResponse = Depends(get_current_admin)
):
    return await user_service.create(data=data)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
        user_id: uuid.UUID,
        _: UserResponse = Depends(get_current_admin)
):
    return await user_service.get_by_id(user_id)

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
        user_id: uuid.UUID,
        data: UserUpdate,
        _: UserResponse = Depends(get_current_admin)
):
    return await user_service.update(user_id, data)