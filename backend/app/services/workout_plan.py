import uuid

from app.core.exceptions import NotAllowedError, WorkoutPlanNotFoundError, UserNotFoundError, \
    WorkoutPlanItemNotFoundError, WorkoutPlanItemAlreadyExistsError, ExerciseNotFoundError
from app.models.user import UserRole, User
from app.models.workout import WorkoutPlan, WorkoutPlanItem, Exercise
from app.schemas.workout_plan import WorkoutPlanItemCreate, WorkoutPlanItemUpdate, WorkoutPlanCreate, WorkoutPlanUpdate
from app.services.exercise import apply_updates


#==========  WORKOUT PLAN ITEM CRUD =================================================================================
async def create_workout_plan_item(plan_id: uuid.UUID, data: WorkoutPlanItemCreate) -> WorkoutPlanItem | None:
    workout_plan = await get_workout_plan_by_id(plan_id)
    exercise = await Exercise.get(data.exercise_id)
    if not exercise:
        raise ExerciseNotFoundError

    existing = await WorkoutPlanItem.find_one(
        {"workout_plan.$id":plan_id, "exercise.$id": data.exercise_id}
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

async def get_workout_plan_item_by_id(w_id: uuid.UUID) -> WorkoutPlanItem:
    item = await WorkoutPlanItem.get(w_id, fetch_links=True)
    if not item:
        raise WorkoutPlanItemNotFoundError()
    return item

async def get_workout_plan_items(w_id: uuid.UUID) -> list[WorkoutPlanItem]:
    items: list[WorkoutPlanItem] = await WorkoutPlanItem.find(
        {"workout_plan.$id": w_id}, fetch_links=True
    ).to_list()
    return items

async def update_workout_plan_item(w_id: uuid.UUID, data: WorkoutPlanItemUpdate) -> WorkoutPlanItem | None:
    item = await get_workout_plan_item_by_id(w_id)

    return await apply_updates(item, data)

async def delete_workout_plan_item(w_id: uuid.UUID) -> None:
    item = await get_workout_plan_item_by_id(w_id)
    await item.delete()

#==========  WORKOUT PLAN CRUD  =============================================================================
async def create_workout_plan(data: WorkoutPlanCreate) -> WorkoutPlan:
    created_by = None
    if data.created_by:
        created_by = await User.get(data.created_by)
        if not created_by:
            raise UserNotFoundError
    plan = WorkoutPlan(
        title=data.title,
        created_by=created_by,  # type: ignore[arg-type]
        level=data.level,
    )
    await plan.insert()
    return plan

async def get_workout_plan_by_id(plan_id: uuid.UUID) -> WorkoutPlan | None:
    plan = await WorkoutPlan.get(plan_id, fetch_links=True)
    if not plan:
        raise WorkoutPlanNotFoundError()
    return plan

async def get_user_workout_plans(user_id: uuid.UUID) -> list[WorkoutPlan]:
    plans: list[WorkoutPlan] = await WorkoutPlan.find(
        {"created_by.$id": user_id}, fetch_links=True
    ).to_list()
    return plans

async def update_workout_plan(plan_id: uuid.UUID, data: WorkoutPlanUpdate, user: User) -> WorkoutPlan | None:
    plan = await get_workout_plan_by_id(plan_id)
    if user.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN) and (not isinstance(plan.created_by, User) or plan.created_by.id != user.id):
        raise NotAllowedError()
    return await apply_updates(plan, data)

async def delete_workout_plan(plan_id: uuid.UUID, user: User) -> None:
    plan = await get_workout_plan_by_id(plan_id)
    if user.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN) and (not isinstance(plan.created_by, User) or plan.created_by.id != user.id):
        raise NotAllowedError()
    await plan.delete()