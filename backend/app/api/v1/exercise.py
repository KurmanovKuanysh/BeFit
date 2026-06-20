import uuid

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_current_admin
from app.models.user import User
from app.schemas.exercise import ExerciseResponse, ExerciseCreate, FilterExercise, ExerciseUpdate
from app.services import exercise as exercise_service


router = APIRouter(prefix="/exercise" ,tags=["Exercises"])


#=====  EXERCISES ========================================

@router.post(path="", response_model=ExerciseResponse)
async def create_exercise(
        data: ExerciseCreate,
        _: User = Depends(get_current_admin),
):
    return await exercise_service.create_exercise(data=data)

@router.get(path="", response_model=list[ExerciseResponse])
async def get_exercises(
        filters: FilterExercise = Depends(),
        _: User = Depends(get_current_user),
):
    return await exercise_service.get_exercises_by_filter(filters=filters)

@router.get("/{id_}", response_model=ExerciseResponse)
async def get_exercise_by_id(
        id_: uuid.UUID,
        _: User = Depends(get_current_user),
):
    return await exercise_service.get_exercise_by_id(id_)

@router.patch("/{id_}", response_model=ExerciseResponse)
async def update_exercise(
        id_: uuid.UUID,
        data: ExerciseUpdate,
        _: User = Depends(get_current_admin),
):
    return await exercise_service.update_exercise(id_, data)

@router.delete("/{id_}", status_code=204)
async def delete_exercise(
        id_: uuid.UUID,
        _: User = Depends(get_current_admin),
):
    await exercise_service.delete_exercise(id_)

