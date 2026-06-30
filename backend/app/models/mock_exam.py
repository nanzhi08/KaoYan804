from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from ..database import Base
from ..time_utils import utc_now_naive


class MockExam(Base):
    __tablename__ = "mock_exams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String(200), nullable=False)
    config = Column(JSON, nullable=False)  # {total_score, time_limit, question_ids, ...}
    score = Column(Float, nullable=True)
    total_score = Column(Integer, default=150)
    time_taken = Column(Integer, nullable=True)  # seconds
    answers = Column(JSON, nullable=True)  # [{question_id, answer, score}, ...]
    status = Column(String(20), default="pending")  # "pending" | "in_progress" | "completed"
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now_naive)
