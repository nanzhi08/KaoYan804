from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text
from ..database import Base
from ..time_utils import utc_now_naive


class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider = Column(String(30), nullable=False)  # "deepseek"
    model = Column(String(50), default="")
    title = Column(String(200), default="新对话")
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=True)
    messages = Column(JSON, default=list)  # [{role, content}, ...]
    created_at = Column(DateTime, default=utc_now_naive)
    updated_at = Column(DateTime, default=utc_now_naive, onupdate=utc_now_naive)
