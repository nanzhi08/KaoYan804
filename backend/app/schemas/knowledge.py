from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class KnowledgePointOut(BaseModel):
    id: int
    parent_id: Optional[int] = None
    name: str
    description: str = ""
    part: str
    chapter: str = ""
    order: int = 0
    difficulty: int = 3
    exam_weight: str = "中频"
    ai_explanation: str = ""
    children: list["KnowledgePointOut"] = []

    class Config:
        from_attributes = True


class KnowledgePointDetail(KnowledgePointOut):
    ai_explanation: str = ""
    created_at: datetime

    class Config:
        from_attributes = True
