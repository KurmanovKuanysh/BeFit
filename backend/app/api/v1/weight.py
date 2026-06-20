import uuid

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.weight import WeightCreate, WeightGraphResponse, WeightResponse, WeightUpdate
from fastapi import APIRouter, Depends

from app.services import weight as weight_service

router = APIRouter(prefix="/weight", tags=["Weight"])

@router.post("", response_model=WeightResponse)
async def create_weight_log(
        data: WeightCreate,
        current_user: User = Depends(get_current_user)
):
    return await weight_service.create_weight_log(data, current_user)

@router.get("", response_model=list[WeightResponse])
async def get_user_weight_logs(
        current_user: User = Depends(get_current_user)
):
    return await weight_service.get_user_weight_logs(current_user.id)

@router.get("/graph", response_model=list[WeightResponse])
async def get_user_weight_logs_graph(
        current_user: User = Depends(get_current_user),
        start_date: str | None = None,
        end_date: str | None = None,
):
    return await weight_service.get_user_weight_graph(current_user, start_date, end_date)

@router.get("/{id_}", response_model=WeightResponse)
async def get_weight_log_by_id(
        id_: uuid.UUID,
        current_user: User = Depends(get_current_user)
):
    return await weight_service.get_user_weight_log_by_id(id_, current_user)

@router.patch("/{id_}", response_model=WeightResponse)
async def update_weight_log(
        id_: uuid.UUID,
        data: WeightUpdate,
        current_user: User = Depends(get_current_user)
):
    return await weight_service.update_weight_log(id_, data, current_user)

@router.delete("/{id_}", status_code=204)
async def delete_weight_log(
        id_: uuid.UUID,
        current_user: User = Depends(get_current_user)
):
    await weight_service.delete_weight_log(id_, current_user)