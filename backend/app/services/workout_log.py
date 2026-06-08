import uuid

from app.core.exceptions import UserNotFoundError, WorkoutDataEmptyError, WorkoutPlanNotFoundError, \
    WorkoutLogNotFoundError, ExerciseNotFoundError, WorkoutLogItemNotFoundError
from app.models.user import User
from app.models.workout import WorkoutLog, WorkoutPlan, WorkoutLogItem, Exercise
from app.schemas.workout_log import WorkoutLogCreate, WorkoutLogUpdate, WorkoutLogItemCreate, WorkoutLogItemUpdate
from app.services.exercise import apply_updates


# ==========  WORKOUT LOG CRUD =============================================================================================
async def create_workout_log(data: WorkoutLogCreate) -> WorkoutLog:
    user = await User.get(data.user_id)
    if not user:
        raise UserNotFoundError

    title = data.title.strip()
    if not title:
        raise WorkoutDataEmptyError("Title cannot be empty")

    workout_log = WorkoutLog(
        title=title.capitalize(),
        user=user,  # type: ignore[arg-type]
    )

    if data.workout_plan_id is not None:
        workout_plan = await WorkoutPlan.get(data.workout_plan_id)
        if not workout_plan:
            raise WorkoutPlanNotFoundError(f"Workout plan with id {data.workout_plan_id} not found")
        workout_log.workout_plan = workout_plan  # type: ignore[arg-type]

    await workout_log.insert()
    return workout_log

async def get_workout_log_by_id(log_id: uuid.UUID) -> WorkoutLog:
    workout_log = await WorkoutLog.get(log_id, fetch_links=True)
    if workout_log is None:
        raise WorkoutLogNotFoundError()
    return workout_log

async def get_workout_logs_by_user_id(user_id: uuid.UUID) -> list[WorkoutLog]:
    logs: list[WorkoutLog] = await WorkoutLog.find(
        {"user.$id": user_id}, fetch_links=True
    ).to_list()
    return logs

async def update_workout_log(log_id: uuid.UUID, data: WorkoutLogUpdate) -> WorkoutLog:
    workout_log = await get_workout_log_by_id(log_id)

    changes = data.model_dump(exclude_unset=True)

    if 'workout_plan_id' in changes:
        wp_id = changes.pop('workout_plan_id')
        if wp_id is not None:
            workout_plan = await WorkoutPlan.get(wp_id)
            if not workout_plan:
                raise WorkoutPlanNotFoundError()
            workout_log.workout_plan = workout_plan  # type: ignore[arg-type]
        else:
            workout_log.workout_plan = None

    for field, value in changes.items():
        setattr(workout_log, field, value)

    await workout_log.save()
    return workout_log

async def delete_workout_log(log_id: uuid.UUID) -> None:
    workout_log = await get_workout_log_by_id(log_id)
    await workout_log.delete()

#==========  WORKOUT LOG ITEM CRUD =============================================================================================

async def create_workout_log_item(data: WorkoutLogItemCreate) -> WorkoutLogItem | None:
    workout_log = await WorkoutLog.get(data.workout_log_id)
    if not workout_log:
        raise WorkoutLogNotFoundError

    exercise = await Exercise.get(data.exercise_id)
    if not exercise:
        raise ExerciseNotFoundError

    workout_item = WorkoutLogItem(
        workout_log=workout_log,  # type: ignore[arg-type]
        exercise=exercise,  # type: ignore[arg-type]
        sets=data.sets,
        reps=data.reps,
    )

    if data.weight is not None:
        workout_item.weight = data.weight
    if data.duration_seconds is not None:
        workout_item.duration_seconds = data.duration_seconds

    await workout_item.insert()
    return workout_item

async def get_workout_log_item_by_id(w_id: uuid.UUID) -> WorkoutLogItem:
    item = await WorkoutLogItem.get(w_id, fetch_links=True)
    if not item:
        raise WorkoutLogItemNotFoundError
    return item

async def get_workout_log_items(w_id: uuid.UUID) -> list[WorkoutLogItem]:
    items: list[WorkoutLogItem] = await WorkoutLogItem.find(
        {"workout_log.$id": w_id}, fetch_links=True
    ).to_list()
    return items

async def update_workout_log_item(
        log_item_id: uuid.UUID,
        data: WorkoutLogItemUpdate
) -> WorkoutLogItem:
    item = await get_workout_log_item_by_id(log_item_id)

    return await apply_updates(item, data)

async def delete_workout_log_item(w_id: uuid.UUID) -> None:
    item = await get_workout_log_item_by_id(w_id)
    await item.delete()

