import uuid
from datetime import datetime

from app.core.exceptions import UserNotFoundError, WaterLogNotFoundError, NotAllowedError
from app.models.user import User, UserRole
from app.models.water import Water
from app.schemas.water import WaterCreate, WaterUpdate


async def create_water_log(
        data: WaterCreate,
        user: User
) -> Water:
    log = Water(
        user=user,  # type: ignore[arg-type]
        amount_ml=data.amount_ml
    )

    await log.insert()
    return log

async def get_user_water_logs(user_id: uuid.UUID) -> list[Water]:
    return await Water.find(
        Water.user.id == user_id,
        fetch_links=True# type: ignore[attr-defined]
    ).to_list()

async def get_user_water_log_by_date(
        user_id: uuid.UUID,
        date_from: datetime,
        date_to: datetime | None = None
):
    if date_to is None:
        date_to = datetime.now()

    return await Water.find(
        Water.user.id == user_id,  # type: ignore[attr-defined]
        Water.created_at >= date_from,
        Water.created_at <= date_to,
        fetch_links=True
    ).to_list()

async def get_water_log_by_id(
        log_id: uuid.UUID,
        user: User
) -> Water:
    log = await Water.get(log_id, fetch_links=True)
    if not log:
        raise WaterLogNotFoundError()

    if not isinstance(log.user, User):
        await log.fetch_link(Water.user)

    ensure_owner_or_admin(log.user.id, user)
    return log

async def update_water_log(
        log_id: uuid.UUID,
        data: WaterUpdate,
        user: User
) -> Water:
    log = await get_water_log_by_id(log_id, user)
    log.amount_ml = data.amount_ml
    await log.save()

    return log

async def delete_water_log(
        log_id: uuid.UUID,
        user: User
) -> None:
    log = await get_water_log_by_id(log_id, user)
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
