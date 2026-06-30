from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship
from ..database import Base
from ..time_utils import utc_now_naive


class KnowledgeMastery(Base):
    __tablename__ = "knowledge_mastery"
    __table_args__ = (UniqueConstraint("user_id", "knowledge_point_id", name="uq_user_knowledge_point"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=False)
    mastery_level = Column(Float, default=0.0)  # 0.0 ~ 1.0
    ease_factor = Column(Float, default=2.5)     # SM-2 parameter
    interval_days = Column(Integer, default=0)
    repetitions = Column(Integer, default=0)
    total_attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)
    last_reviewed_at = Column(DateTime, nullable=True)
    next_review_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=utc_now_naive, onupdate=utc_now_naive)

    knowledge_point = relationship("KnowledgePoint", back_populates="mastery")
