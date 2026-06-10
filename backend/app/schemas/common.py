from typing import TypeVar, Generic

from pydantic import BaseModel

T =TypeVar('T')

class Paginated(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int