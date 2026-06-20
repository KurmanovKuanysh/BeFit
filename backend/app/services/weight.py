import uuid
from datetime import datetime, timezone, timedelta

from app.core.exceptions import WeightLogNotFoundError, NotAllowedError
from app.models.user import User, UserRole
from app.models.weight_log import WeightLog
from app.schemas.weight import WeightCreate, WeightGraphResponse, WeightUpdate
from app.services.exercise import apply_updates


async def create_weight_log(
        data: WeightCreate,
        user: User
) -> WeightLog:
    log = WeightLog(
        user=user, # type: ignore[arg-type]
        weight=data.weight,
    )
    if data.notes is not None:
        log.notes = data.notes.strip()

    await log.insert()
    return log

async def get_user_weight_graph(
        user: User,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
) -> WeightGraphResponse:
    if not end_date:
        end_date = datetime.now(timezone.utc)
    if not start_date:
        start_date = end_date - timedelta(days=7)

    query = WeightLog.find_many(
        WeightLog.user.id == user.id,  # type: ignore[attr-defined]
        WeightLog.created_at >= start_date,
        WeightLog.created_at <= end_date,
    )

    items = await query.to_list()
    total_points = len(items)

    return WeightGraphResponse(
        items=items,
        total_points=total_points,
        start_date=start_date,
        end_date=end_date,
    )
async def get_user_weight_logs(
        user_id: uuid.UUID,
) -> list[WeightLog]:
    return await WeightLog.find_many(
        WeightLog.user.id == user_id,  # type: ignore[attr-defined]
        fetch_links=True
    ).to_list()

async def get_user_weight_log_by_id(
        log_id: uuid.UUID,
        user: User
) -> WeightLog:
    log = await WeightLog.get(log_id, fetch_links=True)
    if not log:
        raise WeightLogNotFoundError()
    if not isinstance(log.user, User):
        await log.fetch_link(WeightLog.user)

    ensure_owner_or_admin(log.user.id, user)
    return log

async def update_weight_log(
        log_id:uuid.UUID,
        data: WeightUpdate,
        user: User
) -> WeightLog:
    log = await get_user_weight_log_by_id(log_id, user)
    return await apply_updates(log, data)

async def delete_weight_log(
        log_id: uuid.UUID,
        user: User
) -> None:
    log = await get_user_weight_log_by_id(log_id, user)
    await log.delete()

#======== Helper===========
def ensure_owner_or_admin(
        data_user_id: uuid.UUID,
        current_user: User
) -> None:
    if current_user.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
        return
    if data_user_id != current_user.id:
        raise NotAllowedError()
