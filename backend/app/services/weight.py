import uuid
from datetime import datetime, timezone, timedelta

from app.core.exceptions import UserNotFoundError
from app.models.user import User
from app.models.weight_log import WeightLog
from app.schemas.weight import WeightCreate, WeightGraphResponse


async def create_weight_log(data: WeightCreate) -> WeightLog:
    user = User.get(data.user_id)
    if not user:
        raise UserNotFoundError
    log = WeightLog(
        user=user, # type: ignore[arg-type]
        weight=data.weight,
    )
    if data.notes is not None:
        log.notes = data.notes.strip()

    await log.insert()
    return log

async def get_user_weight_graph(
        user_id: uuid.UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
) -> WeightGraphResponse:
    if not end_date:
        end_date = datetime.now(timezone.utc)
    if not start_date:
        start_date = end_date - timedelta(days=7)

    query = WeightLog.find({
            "user.$id": user_id,
            "created_at": {
                "$gte": start_date,
                "$lte": end_date,
            }
        })

    items = await query.to_list()
    total_points = len(items)

    return WeightGraphResponse(
        items=items,
        total_points=total_points,
        start_date=start_date,
        end_date=end_date,
    )

