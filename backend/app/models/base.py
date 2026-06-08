import uuid
from datetime import datetime, timezone
from pydantic import Field
from beanie import before_event, Replace, Update, SaveChanges


class TimeStampMixin:
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @before_event(Replace, Update, SaveChanges)
    def update_timestamp(self):
        self.updated_at = datetime.now(timezone.utc)


class UUIDPrimaryKeyMixin:
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
