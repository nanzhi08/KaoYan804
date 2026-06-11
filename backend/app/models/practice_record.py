from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
from ..time_utils import utc_now_naive


class PracticeRecord(Base):
    __tablename__ = "practice_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    user_answer = Column(String(5000), nullable=False)
    is_correct = Column(Boolean, default=False)
    time_spent = Column(Integer, default=0)  # seconds
    practice_mode = Column(String(20), default="random")  # "random" | "chapter" | "review" | "exam"
    created_at = Column(DateTime, default=utc_now_naive)

    question = relationship("Question", lazy="selectin")
