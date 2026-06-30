from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from ..database import Base
from ..time_utils import utc_now_naive


class AITrainingExample(Base):
    __tablename__ = "ai_training_examples"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    conversation_id = Column(Integer, ForeignKey("ai_conversations.id"), nullable=True)
    feedback_id = Column(Integer, ForeignKey("ai_feedbacks.id"), nullable=True)
    user_question = Column(Text, nullable=False)
    assistant_answer = Column(Text, nullable=False)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=True)
    chapter = Column(String(20), default="")
    part = Column(String(50), default="")
    keywords = Column(Text, default="")
    usage_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now_naive)
