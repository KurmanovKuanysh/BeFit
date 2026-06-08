from beanie import Document, Link
from app.models.base import TimeStampMixin, UUIDPrimaryKeyMixin
from app.models.user import User


class WeightLog(UUIDPrimaryKeyMixin, TimeStampMixin, Document):
    user: Link[User]
    weight: float
    notes: str | None = None

    class Settings:
        name = "weight_logs"

        indexes = [
            "user",
        ]