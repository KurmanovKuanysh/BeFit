import uuid

from app.core.exceptions import WorkoutPlanNotFoundError, \
    WorkoutPlanItemNotFoundError, WorkoutPlanItemAlreadyExistsError, ExerciseNotFoundError
from app.models.user import User
from app.models.workout import WorkoutPlan, WorkoutPlanItem, Exercise
from app.schemas.workout_plan import WorkoutPlanItemCreate, WorkoutPlanItemUpdate, WorkoutPlanCreate, WorkoutPlanUpdate
from app.services.exercise import apply_updates
from app.services.permissions import ensure_owner_or_admin


#==========  WORKOUT PLAN ITEM CRUD =================================================================================
async def create_workout_plan_item(
        plan_id: uuid.UUID,
        data: WorkoutPlanItemCreate,
        user: User
) -> WorkoutPlanItem | None:
    workout_plan = await get_workout_plan_by_id(plan_id, user)
    exercise = await Exercise.get(data.exercise_id)
    if not exercise:
        raise ExerciseNotFoundError()

    existing = await WorkoutPlanItem.find_one(
        WorkoutPlanItem.workout_plan.id == plan_id,  # type: ignore[attr-defined]
        WorkoutPlanItem.exercise.id == data.exercise_id,  # type: ignore[attr-defined]
    )
    if existing:
        raise WorkoutPlanItemAlreadyExistsError()

    item = WorkoutPlanItem(
        workout_plan=workout_plan,  # type: ignore[arg-type]
        exercise=exercise,  # type: ignore[arg-type]
        sets=data.sets,
        reps=data.reps,
        weight=data.weight,
        duration_seconds=data.duration_seconds,
    )
    await item.insert()
    return item

async def get_workout_plan_item_by_id(
        w_id: uuid.UUID,
        item_id: uuid.UUID,
        user: User
) -> WorkoutPlanItem:
    await get_workout_plan_by_id(w_id, user)

    item = await WorkoutPlanItem.find_one(
        WorkoutPlanItem.id == item_id,
        WorkoutPlanItem.workout_plan.id == w_id,  # type: ignore[attr-defined]
        fetch_links=True
    )
    if not item:
        raise WorkoutPlanItemNotFoundError()
    return item

async def get_workout_plan_items(
        w_id: uuid.UUID,
        user: User
) -> list[WorkoutPlanItem]:
    await get_workout_plan_by_id(w_id, user)

    items: list[WorkoutPlanItem] = await WorkoutPlanItem.find(
        WorkoutPlanItem.workout_plan.id == w_id,  # type: ignore[attr-defined]
        fetch_links=True
    ).to_list()
    return items

async def update_workout_plan_item(
        w_id: uuid.UUID,
        item_id: uuid.UUID,
        data: WorkoutPlanItemUpdate,
        user: User
) -> WorkoutPlanItem | None:
    item = await get_workout_plan_item_by_id(w_id, item_id, user)

    return await apply_updates(item, data)

async def delete_workout_plan_item(
        w_id: uuid.UUID,
        item_id: uuid.UUID,
        user: User
) -> None:
    item = await get_workout_plan_item_by_id(w_id, item_id, user)
    await item.delete()

#==========  WORKOUT PLAN CRUD  =============================================================================
async def create_workout_plan(
        data: WorkoutPlanCreate,
        user: User
) -> WorkoutPlan:
    plan = WorkoutPlan(
        title=data.title,
        created_by=user,  # type: ignore[arg-type]
        level=data.level,
        private=data.private,
    )
    await plan.insert()
    return plan

async def list_public_workout_plans() -> list[WorkoutPlan]:
    return await WorkoutPlan.find(
        {"private": False},
    ).to_list()

async def get_workout_plan_by_id(
        plan_id: uuid.UUID,
        user: User
) -> WorkoutPlan | None:
    plan = await WorkoutPlan.get(plan_id, fetch_links=True)
    if not plan:
        raise WorkoutPlanNotFoundError()

    if not isinstance(plan.created_by, User):
        await plan.fetch_link(WorkoutPlan.created_by)

    if plan.private:
        ensure_owner_or_admin(plan.created_by.id, user)

    return plan

async def get_user_workout_plans(
        user_id: uuid.UUID | None,
        my: bool,
        user: User
) -> list[WorkoutPlan]:
    if my:
        return await WorkoutPlan.find_many(
            WorkoutPlan.created_by.id == user.id,  # type: ignore[attr-defined]
        ).to_list()


    if user_id:
        return await WorkoutPlan.find(
            WorkoutPlan.created_by.id == user_id,  # type: ignore[attr-defined]
            WorkoutPlan.private == False,
            fetch_links=True
        ).to_list()


    return await list_public_workout_plans()

async def update_workout_plan(
        plan_id: uuid.UUID,
        data: WorkoutPlanUpdate,
        user: User
) -> WorkoutPlan | None:
    plan = await get_workout_plan_by_id(plan_id, user)
    return await apply_updates(plan, data)

async def delete_workout_plan(
        plan_id: uuid.UUID,
        user: User
) -> None:
    plan = await get_workout_plan_by_id(plan_id, user)

    await plan.delete()

