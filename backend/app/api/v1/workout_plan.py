import uuid

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.workout_plan import WorkoutPlanResponse, WorkoutPlanCreate, WorkoutPlanUpdate, WorkoutPlanItemCreate, \
    WorkoutPlanItemResponse, WorkoutPlanItemUpdate
from app.services import workout_plan as workout_plan_service

router = APIRouter(prefix="/workout-plans", tags=["Workout"])

#=====  WORKOUT PLANS  ========================================

@router.post("", response_model=WorkoutPlanResponse)
async def create_workout_plan(
        data: WorkoutPlanCreate,
        current_user: User = Depends(get_current_user),
):
    return await workout_plan_service.create_workout_plan(data, current_user)

@router.get("", response_model=list[WorkoutPlanResponse])
async def get_user_workout_plans(
        user_id: uuid.UUID | None = None,
        my: bool = False,
        current_user: User = Depends(get_current_user),
):
    return await workout_plan_service.get_user_workout_plans(user_id=user_id, my=my, user=current_user)

@router.get("/{id_}", response_model=WorkoutPlanResponse)
async def get_workout_plan_by_id(
        id_: uuid.UUID,
        current_user: User = Depends(get_current_user),
):
    return await workout_plan_service.get_workout_plan_by_id(id_, current_user)

@router.patch("/{id_}", response_model=WorkoutPlanResponse)
async def update_workout_plan(
        id_: uuid.UUID,
        data: WorkoutPlanUpdate,
        current_user: User = Depends(get_current_user),
):
    return await workout_plan_service.update_workout_plan(plan_id=id_, data=data, user=current_user)

@router.delete("/{id_}", status_code=204)
async def delete_workout_plan(
        id_: uuid.UUID,
        current_user: User = Depends(get_current_user),
):
    await workout_plan_service.delete_workout_plan(plan_id=id_, user=current_user)

#=====  WORKOUT PLAN ITEMS  ========================================

@router.post("/{id_}/items", response_model=WorkoutPlanItemResponse)
async def create_workout_plan_item(
        id_: uuid.UUID,
        data: WorkoutPlanItemCreate,
        current_user: User = Depends(get_current_user),
):
    return await workout_plan_service.create_workout_plan_item(plan_id=id_, data=data, user=current_user)

@router.get("/{id_}/items", response_model=list[WorkoutPlanItemResponse])
async def get_workout_plan_items(
        id_: uuid.UUID,
        current_user: User = Depends(get_current_user),
):
    return await workout_plan_service.get_workout_plan_items(id_, current_user)

@router.get("/{id_}/items/{item_id_}", response_model=WorkoutPlanItemResponse)
async def get_workout_plan_item(
        id_: uuid.UUID,
        item_id_: uuid.UUID,
        current_user: User = Depends(get_current_user),
):
    return await workout_plan_service.get_workout_plan_item_by_id(id_, item_id_, current_user)

@router.patch("/{id_}/items/{item_id_}", response_model=WorkoutPlanItemResponse)
async def update_workout_plan_item(
        id_: uuid.UUID,
        item_id_: uuid.UUID,
        data: WorkoutPlanItemUpdate,
        current_user: User = Depends(get_current_user),
):
    return await workout_plan_service.update_workout_plan_item(id_, item_id_, data, current_user)

@router.delete("/{id_}/items/{item_id_}", status_code=204)
async def delete_workout_plan_item(
        id_: uuid.UUID,
        item_id_: uuid.UUID,
        current_user: User = Depends(get_current_user),
):
    await workout_plan_service.delete_workout_plan_item(id_, item_id_, current_user)

