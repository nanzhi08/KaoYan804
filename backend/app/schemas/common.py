from pydantic import BaseModel
from typing import Any


class APIResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None


class PaginatedData(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int
