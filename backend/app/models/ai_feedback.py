from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from datetime import datetime
from ..database import Base


class AIFeedback(Base):
    __tablename__ = "ai_feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("ai_conversations.id"), nullable=False, index=True)
    message_id = Column(String(64), nullable=False, index=True)
    message_index = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=False)  # 1 = thumbs up, -1 = thumbs down
    comment = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
