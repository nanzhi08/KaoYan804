from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    part: str
    difficulty: int = 3
    content: str
    options: Optional[dict] = None
    answer: str
    explanation: str = ""
    source: Optional[str] = None
    code_snippet: Optional[str] = None
    knowledge_point_ids: list[int] = []


class QuestionListParams(BaseModel):
    type: Optional[str] = None
    part: Optional[str] = None
    difficulty: Optional[int] = None
    knowledge_point_id: Optional[int] = None
    page: int = 1
    page_size: int = 20


class QuestionCreate(BaseModel):
    type: str
    part: str
    difficulty: int = 3
    content: str
    options: Optional[dict] = None
    answer: str
    explanation: str = ""
    source: Optional[str] = None
    code_snippet: Optional[str] = None
    knowledge_point_ids: list[int] = []


class PracticeSubmit(BaseModel):
    question_id: int
    user_answer: str
    time_spent: int = 0
    practice_mode: str = "random"


class PracticeResult(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: str = ""
