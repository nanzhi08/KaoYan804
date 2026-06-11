from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class KnowledgePointOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class KnowledgePointDetail(KnowledgePointOut):
    ai_explanation: str = ""
    created_at: datetime
