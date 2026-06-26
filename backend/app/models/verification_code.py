import pymongo
from beanie import Document, Link
from pydantic import Field
from pymongo import IndexModel

from app.models.base import TimeStampMixin, UUIDPrimaryKeyMixin
from app.models.user import User


class VerificationCode(UUIDPrimaryKeyMixin,TimeStampMixin, Document):
    code: int = Field(ge=100000, le=999999)
    user: Link[User]

    class Settings:
        name = "verification_codes"
        indexes = [
            "user",
            IndexModel(
                [("created_at", pymongo.ASCENDING)],
                name="created_at_ttl_index",
                expireAfterSeconds=600,
            ),
        ]