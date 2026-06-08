import uuid

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_current_admin
from app.models.user import User
from app.schemas.exercise import ExerciseResponse, ExerciseCreate, FilterExercise, ExerciseUpdate
from app.schemas.workout_plan import WorkoutPlanResponse, WorkoutPlanCreate, WorkoutPlanUpdate, WorkoutPlanItemCreate, \
    WorkoutPlanItemResponse, WorkoutPlanItemUpdate

from app.schemas.workout_log import WorkoutLogResponse, WorkoutLogCreate, WorkoutLogUpdate, WorkoutLogItemCreate, \
    WorkoutLogItemResponse, WorkoutLogItemUpdate

from app.services import exercise as exercise_service
from app.services import workout_plan as workout_plan_service
from app.services import workout_log as workout_log_service

router = APIRouter(tags=["Workout, Exercises, Workout Logs"])


#=====  EXERCISES ========================================

@router.post("/exercises", response_model=ExerciseResponse, status_code=201)
async def create_exercise(
        data: ExerciseCreate,
        _: User = Depends(get_current_admin),
):
    return await exercise_service.create_exercise(data=data)

@router.get("/exercises", response_model=list[ExerciseResponse], status_code=200)
async def get_exercises(
        filters: FilterExercise = Depends(),
        _: User = Depends(get_current_user),
):
    return await exercise_service.get_exercises_by_filter(filters=filters)

@router.get("/exercises/{id_}", response_model=ExerciseResponse, status_code=200)
async def get_exercise_by_id(
        id_: uuid.UUID,
        _: User = Depends(get_current_user),
):
    return await exercise_service.get_exercise_by_id(id_)

@router.patch("/exercises/{id_}", response_model=ExerciseResponse, status_code=200)
async def update_exercise(
        id_: uuid.UUID,
        data: ExerciseUpdate,
        _: User = Depends(get_current_admin),
):
    return await exercise_service.update_exercise(id_, data)

@router.delete("/exercises/{id_}", status_code=204)
async def delete_exercise(
        id_: uuid.UUID,
        _: User = Depends(get_current_admin),
):
    await exercise_service.delete_exercise(id_)


#=====  WORKOUT PLANS  ========================================

@router.post("/workout-plans", response_model=WorkoutPlanResponse, status_code=201)
async def create_workout_plan(
        data: WorkoutPlanCreate,
        current_user: User = Depends(get_current_user),
):
    data.created_by = current_user.id
    return await workout_plan_service.create_workout_plan(data=data)

@router.get("/workout-plans/my", response_model=list[WorkoutPlanResponse], status_code=200)
async def get_user_workout_plans(
        current_user: User = Depends(get_current_user),
):
    return await workout_plan_service.get_user_workout_plans(user_id=current_user.id)

@router.get("/workout-plans/{id_}", response_model=WorkoutPlanResponse, status_code=200)
async def get_workout_plan_by_id(
        id_: uuid.UUID,
        _: User = Depends(get_current_user),
):
    return await workout_plan_service.get_workout_plan_by_id(id_)

@router.patch("/workout-plans/{id_}", response_model=WorkoutPlanResponse, status_code=200)
async def update_workout_plan(
        id_: uuid.UUID,
        data: WorkoutPlanUpdate,
        current_user: User = Depends(get_current_user),
):
    return await workout_plan_service.update_workout_plan(plan_id=id_, data=data, user=current_user)

@router.delete("/workout-plans/{id_}", status_code=204)
async def delete_workout_plan(
        id_: uuid.UUID,
        current_user: User = Depends(get_current_user),
):
    await workout_plan_service.delete_workout_plan(plan_id=id_, user=current_user)

#=====  WORKOUT PLAN ITEMS  ========================================

@router.post("/workout-plans/{id_}/items", response_model=WorkoutPlanItemResponse, status_code=201)
async def create_workout_plan_item(
        id_: uuid.UUID,
        data: WorkoutPlanItemCreate,
        _: User = Depends(get_current_user),
):
    return await workout_plan_service.create_workout_plan_item(plan_id=id_, data=data)

@router.get("/workout-plans/{id_}/items", response_model=list[WorkoutPlanItemResponse], status_code=200)
async def get_workout_plan_items(
        id_: uuid.UUID,
        _: User = Depends(get_current_user),
):
    return await workout_plan_service.get_workout_plan_items(id_)

@router.get("/workout-plans/{id_}/items/{item_id_}", response_model=WorkoutPlanItemResponse, status_code=200)
async def get_workout_plan_item(
        id_: uuid.UUID,
        item_id_: uuid.UUID,
        _: User = Depends(get_current_user),
):
    return await workout_plan_service.get_workout_plan_item_by_id(item_id_)

@router.patch("/workout-plans/{id_}/items/{item_id_}", response_model=WorkoutPlanItemResponse, status_code=200)
async def update_workout_plan_item(
        id_: uuid.UUID,
        item_id_: uuid.UUID,
        data: WorkoutPlanItemUpdate,
        _: User = Depends(get_current_user),
):
    return await workout_plan_service.update_workout_plan_item(item_id_, data)

@router.delete("/workout-plans/{id_}/items/{item_id_}", status_code=204)
async def delete_workout_plan_item(
        id_: uuid.UUID,
        item_id_: uuid.UUID,
        _: User = Depends(get_current_user),
):
    await workout_plan_service.delete_workout_plan_item(item_id_)


#=====  WORKOUT LOGS  ========================================

@router.post("/workout-logs", response_model=WorkoutLogResponse, status_code=201)
async def create_workout_log(
        data: WorkoutLogCreate,
        current_user: User = Depends(get_current_user),
):
    data.user_id = current_user.id
    return await workout_log_service.create_workout_log(data=data)

@router.get("/workout-logs/my", response_model=list[WorkoutLogResponse], status_code=200)
async def get_user_workout_logs(
        current_user: User = Depends(get_current_user),
):
    return await workout_log_service.get_workout_logs_by_user_id(user_id=current_user.id)

@router.get("/workout-logs/{id_}", response_model=WorkoutLogResponse, status_code=200)
async def get_workout_log_by_id(
        id_: uuid.UUID,
        _: User = Depends(get_current_user),
):
    return await workout_log_service.get_workout_log_by_id(id_)

@router.patch("/workout-logs/{id_}", response_model=WorkoutLogResponse, status_code=200)
async def update_workout_log(
        id_: uuid.UUID,
        data: WorkoutLogUpdate,
        _: User = Depends(get_current_user),
):
    return await workout_log_service.update_workout_log(id_, data)

@router.delete("/workout-logs/{id_}", status_code=204)
async def delete_workout_log(
        id_: uuid.UUID,
        _: User = Depends(get_current_user),
):
    await workout_log_service.delete_workout_log(id_)

#=====  WORKOUT LOG ITEMS  ========================================

@router.post("/workout-logs/{id_}/items", response_model=WorkoutLogItemResponse, status_code=201)
async def create_workout_log_item(
        id_: uuid.UUID,
        data: WorkoutLogItemCreate,
        _: User = Depends(get_current_user),
):
    data.workout_log_id = id_
    return await workout_log_service.create_workout_log_item(data=data)

@router.get("/workout-logs/{id_}/items", response_model=list[WorkoutLogItemResponse], status_code=200)
async def get_workout_log_items(
        id_: uuid.UUID,
        _: User = Depends(get_current_user),
):
    return await workout_log_service.get_workout_log_items(id_)

@router.get("/workout-logs/{id_}/items/{item_id_}", response_model=WorkoutLogItemResponse, status_code=200)
async def get_workout_log_item(
        id_: uuid.UUID,
        item_id_: uuid.UUID,
        _: User = Depends(get_current_user),
):
    return await workout_log_service.get_workout_log_item_by_id(item_id_)

@router.patch("/workout-logs/{id_}/items/{item_id_}", response_model=WorkoutLogItemResponse, status_code=200)
async def update_workout_log_item(
        id_: uuid.UUID,
        item_id_: uuid.UUID,
        data: WorkoutLogItemUpdate,
        _: User = Depends(get_current_user),
):
    return await workout_log_service.update_workout_log_item(item_id_, data)

@router.delete("/workout-logs/{id_}/items/{item_id_}", status_code=204)
async def delete_workout_log_item(
        id_: uuid.UUID,
        item_id_: uuid.UUID,
        _: User = Depends(get_current_user),
):
    await workout_log_service.delete_workout_log_item(item_id_)