from typing import Annotated

from beanie import Document, Link
from pydantic import Field

from app.models.base import TimeStampMixin, UUIDPrimaryKeyMixin
from app.models.user import User


class Water(UUIDPrimaryKeyMixin, TimeStampMixin, Document):
    user: Link[User]

    amount_ml: Annotated[
        int,
        Field(ge=0),
    ]

    class Settings:
        name = "water"
