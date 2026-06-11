from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from ..database import Base
from ..time_utils import utc_now_naive


class KnowledgeMastery(Base):
    __tablename__ = "knowledge_mastery"

    id = Column(Integer, primary_key=True, autoincrement=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), unique=True, nullable=False)
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
