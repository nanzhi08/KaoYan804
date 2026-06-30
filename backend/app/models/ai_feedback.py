from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from ..database import Base
from ..time_utils import utc_now_naive


class AIFeedback(Base):
    __tablename__ = "ai_feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    conversation_id = Column(Integer, ForeignKey("ai_conversations.id"), nullable=False, index=True)
    message_id = Column(String(64), nullable=False, index=True)
    message_index = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=False)  # 1 = thumbs up, -1 = thumbs down
    comment = Column(Text, default="")
    created_at = Column(DateTime, default=utc_now_naive)
