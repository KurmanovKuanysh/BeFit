import uuid

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.water import WaterResponse, WaterCreate, WaterUpdate
from app.services import water as water_service

router = APIRouter(prefix="/water", tags=["Water"])

@router.post("", response_model=WaterResponse)
async def create_water_log(
        data: WaterCreate,
        current_user: User = Depends(get_current_user)
):
    return await water_service.create_water_log(data, current_user)

@router.get("", response_model=list[WaterResponse])
async def get_all_my_water_logs(
        current_user: User = Depends(get_current_user)
):
    return await water_service.get_user_water_logs(user_id=current_user.id)

@router.get("/{id_}", response_model=WaterResponse)
async def get_water_log_by_id(
        id_: uuid.UUID,
        current_user: User = Depends(get_current_user)
):
    return await water_service.get_water_log_by_id(id_, current_user)

@router.patch("/{id_}", response_model=WaterResponse)
async def update_water_log(
        id_: uuid.UUID,
        data: WaterUpdate,
        current_user: User = Depends(get_current_user)
):
    return await water_service.update_water_log(id_, data, current_user)

@router.delete("/{id_}", status_code=204)
async def delete_water_log(
        id_: uuid.UUID,
        current_user: User = Depends(get_current_user)
):
    await water_service.delete_water_log(id_, current_user)