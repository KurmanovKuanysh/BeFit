import uuid

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_current_admin
from app.models.user import User

from app.schemas.workout_log import WorkoutLogResponse, WorkoutLogCreate, WorkoutLogUpdate, WorkoutLogItemCreate, \
    WorkoutLogItemResponse, WorkoutLogItemUpdate

from app.services import workout_log as workout_log_service

router = APIRouter(tags=["Workout Logs"])

#=====  WORKOUT LOGS  ========================================

@router.post("/workout-logs", response_model=WorkoutLogResponse)
async def create_workout_log(
        data: WorkoutLogCreate,
        current_user: User = Depends(get_current_user),
):
    return await workout_log_service.create_workout_log(data, current_user)

@router.get("/workout-logs/my", response_model=list[WorkoutLogResponse])
async def get_user_workout_logs(
        current_user: User = Depends(get_current_user),
):
    return await workout_log_service.get_workout_logs_by_user_id(user_id=current_user.id)

@router.get("/workout-logs/user/{id_}", response_model=list[WorkoutLogResponse])
async def get_workout_logs_by_user_id(
        id_: uuid.UUID,
        current_admin: User = Depends(get_current_admin),
):
    return await workout_log_service.get_workout_logs_by_user_id(user_id=id_)

@router.get("/workout-logs/{id_}", response_model=WorkoutLogResponse)
async def get_workout_log_by_id(
        id_: uuid.UUID,
        current_user: User = Depends(get_current_user),
):
    return await workout_log_service.get_workout_log_by_id(id_, current_user)

@router.patch("/workout-logs/{id_}", response_model=WorkoutLogResponse)
async def update_workout_log(
        id_: uuid.UUID,
        data: WorkoutLogUpdate,
        current_user: User = Depends(get_current_user),
):
    return await workout_log_service.update_workout_log(id_, data, current_user)

@router.delete("/workout-logs/{id_}", status_code=204)
async def delete_workout_log(
        id_: uuid.UUID,
        current_user: User = Depends(get_current_user),
):
    await workout_log_service.delete_workout_log(id_, current_user)

#=====  WORKOUT LOG ITEMS  ========================================

@router.post("/workout-logs/{id_}/items", response_model=WorkoutLogItemResponse)
async def create_workout_log_item(
        id_: uuid.UUID,
        data: WorkoutLogItemCreate,
        current_user: User = Depends(get_current_user),
):
    return await workout_log_service.create_workout_log_item(id_, data, current_user)

@router.get("/workout-logs/{id_}/items", response_model=list[WorkoutLogItemResponse])
async def get_workout_log_items(
        id_: uuid.UUID,
        current_user: User = Depends(get_current_user),
):
    return await workout_log_service.get_workout_log_items(id_, current_user)

@router.get("/workout-logs/{id_}/items/{item_id_}", response_model=WorkoutLogItemResponse)
async def get_workout_log_item(
        id_: uuid.UUID,
        item_id_: uuid.UUID,
        current_user: User = Depends(get_current_user),
):
    return await workout_log_service.get_workout_log_item_by_id(id_, item_id_, current_user)

@router.patch("/workout-logs/{id_}/items/{item_id_}", response_model=WorkoutLogItemResponse)
async def update_workout_log_item(
        id_: uuid.UUID,
        item_id_: uuid.UUID,
        data: WorkoutLogItemUpdate,
        current_user: User = Depends(get_current_user),
):
    return await workout_log_service.update_workout_log_item(id_, item_id_, data, current_user)

@router.delete("/workout-logs/{id_}/items/{item_id_}", status_code=204)
async def delete_workout_log_item(
        id_: uuid.UUID,
        item_id_: uuid.UUID,
        current_user: User = Depends(get_current_user),
):
    await workout_log_service.delete_workout_log_item(id_, item_id_, current_user)