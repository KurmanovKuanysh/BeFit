import uuid
from datetime import datetime

from app.core.exceptions import UserNotFoundError, WaterLogNotFoundError
from app.models.user import User
from app.models.water import Water
from app.schemas.water import WaterCreate, WaterUpdate


async def create_water_log(data: WaterCreate) -> Water:
    user = await User.get(data.user_id)
    if not user:
        raise UserNotFoundError
    log = Water(
        user=user,  # type: ignore[arg-type]
        amount_ml=data.amount
    )

    await log.insert()
    return log

async def get_user_water_logs(user_id: uuid.UUID) -> list[Water]:
    return await Water.find(
        {"user.$id": user_id},
    ).to_list()

async def get_user_water_log_by_date(
        user_id: uuid.UUID,
        date_from: datetime,
        date_to: datetime | None = None
):
    if date_to is None:
        date_to = datetime.now()

    return await Water.find(
        {"user.$id":user_id,
         "date": {"$gte": date_from, "$lte": date_to}
         }
    ).to_list()

async def get_water_log_by_id(log_id: uuid.UUID) -> Water:
    log = await Water.get(log_id)
    if not log:
        raise WaterLogNotFoundError
    return log

async def update_water_log(log_id: uuid.UUID, data: WaterUpdate) -> Water:
    log = await get_water_log_by_id(log_id)
    log.amount_ml = data.amount
    await log.save()

    return log

async def delete_water_log(log_id: uuid.UUID) -> None:
    log = await get_water_log_by_id(log_id)
    await log.delete()