import uuid

from app.core.exceptions import NotAllowedError
from app.models.user import User, UserRole


def ensure_owner_or_admin(
        data_user_id: uuid.UUID,
        current_user: User
) -> None:
    if current_user.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
        return
    if data_user_id != current_user.id:
        raise NotAllowedError()
