import re
import uuid

from app.core.exceptions import ExerciseNotFoundError, ExerciseAlreadyExistsError
from app.models.workout import Exercise
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate, FilterExercise



#==========  EXERCISES CRUD  ================================================================================================
async def get_exercise_by_id(exercise_id: uuid.UUID) -> Exercise | None:
    exercise = await Exercise.get(exercise_id)
    if not exercise:
        raise ExerciseNotFoundError()
    return exercise

async def get_exercise_by_name(exercise_name: str) -> list[Exercise]:
    exercise = await Exercise.find(
        {"name": re.compile(exercise_name, re.IGNORECASE)}
    ).to_list()
    return exercise

async def get_exercises() -> list[Exercise]:
    return await Exercise.find().to_list()

async def get_exercises_by_filter(filters: FilterExercise) -> list[Exercise]:
    query: dict = {}
    if filters.name:
        query["name"] = re.compile(filters.name.strip(), re.IGNORECASE)
    if filters.type:
        query["type"] = filters.type
    if filters.category:
        query["category"] = filters.category
    if filters.level:
        query["level"] = filters.level

    return await Exercise.find(query).to_list()


async def create_exercise(data: ExerciseCreate) -> Exercise | None:
    existing = await Exercise.find(
        {"name": {"$regex": f"^{re.escape(data.name).lower()}", "$options": "i"}}
    ).to_list()
    if existing:
        raise ExerciseAlreadyExistsError()
    exercise = Exercise(
        name=data.name,
        type=data.type,
        description=data.description,
        category=data.category,
        measurement_unit=data.measurement_unit,
        level=data.level,
    )

    await exercise.insert()
    return exercise

async def update_exercise(exercise_id: uuid.UUID, data: ExerciseUpdate) -> Exercise | None:
    exercise = await get_exercise_by_id(exercise_id)

    return await apply_updates(exercise, data)

async def delete_exercise(exercise_id: uuid.UUID) -> None:
    exercise = await get_exercise_by_id(exercise_id)
    await exercise.delete()

#======= Helper ================================================
async def apply_updates(
        obj, data
):
    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(obj, field, value)
    await obj.save()
    return obj