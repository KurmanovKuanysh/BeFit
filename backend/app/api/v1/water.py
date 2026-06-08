import uuid

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.schemas.user import UserResponse
from app.schemas.water import WaterResponse, WaterCreate, WaterUpdate
from app.services import water as water_service

router = APIRouter(prefix="/water", tags=["Water"])

@router.post("", response_model=WaterResponse, status_code=201)
async def create_water(
        data: WaterCreate,
        _: UserResponse = Depends(get_current_user)
):
    return await water_service.create_water_log(data=data)

@router.get("/my", response_model=list[WaterResponse], status_code=200)
async def get_all_my_water_logs(
        _: UserResponse = Depends(get_current_user)
):
    return await water_service.get_user_water_logs(user_id=_.id)

@router.get("/{id_}", response_model=WaterResponse, status_code=200)
async def get_water_log_by_id(
        id_: uuid.UUID,
        _: UserResponse = Depends(get_current_user)
):
    return await water_service.get_water_log_by_id(id_)

@router.patch("/{id_}", response_model=WaterResponse, status_code=200)
async def update_water_log(
        id_: uuid.UUID,
        data: WaterUpdate,
        _: UserResponse = Depends(get_current_user)
):
    return await water_service.update_water_log(id_, data)

@router.delete("/{id_}", status_code=204)
async def delete_water_log(
        id_: uuid.UUID,
        _: UserResponse = Depends(get_current_user)
):
    await water_service.delete_water_log(id_)