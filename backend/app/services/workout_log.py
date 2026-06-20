import uuid

from app.core.exceptions import UserNotFoundError, WorkoutDataEmptyError, WorkoutPlanNotFoundError, \
    WorkoutLogNotFoundError, ExerciseNotFoundError, WorkoutLogItemNotFoundError, NotAllowedError
from app.models.user import User, UserRole
from app.models.workout import WorkoutLog, WorkoutPlan, WorkoutLogItem, Exercise
from app.schemas.workout_log import WorkoutLogCreate, WorkoutLogUpdate, WorkoutLogItemCreate, WorkoutLogItemUpdate
from app.services.exercise import apply_updates


# ==========  WORKOUT LOG CRUD =============================================================================================
async def create_workout_log(
        data: WorkoutLogCreate,
        user: User
) -> WorkoutLog:
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

async def get_workout_log_by_id(
        log_id: uuid.UUID,
        user: User
) -> WorkoutLog:
    workout_log = await WorkoutLog.get(log_id, fetch_links=True)
    if workout_log is None:
        raise WorkoutLogNotFoundError()
    if not isinstance(workout_log.user, User):
        await workout_log.fetch_link(WorkoutLog.user)

    ensure_owner_or_admin(workout_log.user.id, user)

    return workout_log

async def get_workout_logs_by_user_id(
        user_id: uuid.UUID
) -> list[WorkoutLog]:
    logs: list[WorkoutLog] = await WorkoutLog.find(
        WorkoutLog.user.id == user_id, # type: ignore[attr-defined]
        fetch_links=True
    ).to_list()
    return logs

async def update_workout_log(
        log_id: uuid.UUID,
        data: WorkoutLogUpdate,
        user: User
) -> WorkoutLog:
    workout_log = await get_workout_log_by_id(log_id, user)

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

async def delete_workout_log(
        log_id: uuid.UUID,
        user: User
) -> None:
    workout_log = await get_workout_log_by_id(log_id, user)
    await workout_log.delete()

#==========  WORKOUT LOG ITEM CRUD =============================================================================================

async def create_workout_log_item(
        w_log_id: uuid.UUID,
        data: WorkoutLogItemCreate,
        user: User
) -> WorkoutLogItem | None:
    workout_log = await get_workout_log_by_id(w_log_id, user)

    exercise = await Exercise.get(data.exercise_id)
    if not exercise:
        raise ExerciseNotFoundError()

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

async def get_workout_log_item_by_id(
        w_log_id: uuid.UUID,
        w_log_item_id: uuid.UUID,
        user: User
) -> WorkoutLogItem:
    await get_workout_log_by_id(w_log_id, user)

    item = await WorkoutLogItem.find_one(
        WorkoutLogItem.id == w_log_item_id,
        WorkoutLogItem.workout_log.id == w_log_id,  # type: ignore[attr-defined]
        fetch_links=True
    )
    if not item:
        raise WorkoutLogItemNotFoundError()

    return item

async def get_workout_log_items(
        w_id: uuid.UUID,
        user: User
) -> list[WorkoutLogItem]:
    await get_workout_log_by_id(w_id, user)

    items: list[WorkoutLogItem] = await WorkoutLogItem.find(
        WorkoutLogItem.workout_log.id == w_id,  # type: ignore[attr-defined]
        fetch_links=True
    ).to_list()
    return items

async def update_workout_log_item(
        w_log_id: uuid.UUID,
        w_log_item_id: uuid.UUID,
        data: WorkoutLogItemUpdate,
        user: User
) -> WorkoutLogItem:
    item = await get_workout_log_item_by_id(w_log_id, w_log_item_id, user)

    return await apply_updates(item, data)

async def delete_workout_log_item(
        w_log_id: uuid.UUID,
        w_log_item_id: uuid.UUID,
        user: User
) -> None:
    item = await get_workout_log_item_by_id(w_log_id, w_log_item_id, user)
    await item.delete()

#======== Helper===========
def ensure_owner_or_admin(
        data_user_id: uuid.UUID,
        current_user: User
) -> None:
    if current_user.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
        return
    if data_user_id != current_user.id:
        raise NotAllowedError()
