from datetime import datetime

from beanie import Document, Link

from app.models.base import UUIDPrimaryKeyMixin, TimeStampMixin
from app.models.user import User


class RefreshToken(UUIDPrimaryKeyMixin, TimeStampMixin, Document):
    user: Link[User]
    token: str
    is_revoked: bool = False
    expires_at: datetime

    class Settings:
        name = "refresh_tokens"