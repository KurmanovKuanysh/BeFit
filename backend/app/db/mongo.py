import logging

import beanie
import motor
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.user import User
from app.models.token import RefreshToken
from app.models.weight_log import WeightLog
from app.models.workout import Exercise, WorkoutPlan, WorkoutPlanItem, WorkoutLog, WorkoutLogItem
from app.models.water import Water

logger = logging.getLogger(__name__)

async def init_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL, uuidRepresentation="standard")

    await beanie.init_beanie(
        database=client[settings.MONGODB_DB_NAME],
        document_models=[
            User,
            RefreshToken,
            Exercise,
            WorkoutPlan,
            WorkoutPlanItem,
            WorkoutLog,
            WorkoutLogItem,
            Water,
            WeightLog
        ]
    )
