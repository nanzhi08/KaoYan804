from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from ..database import Base
from ..time_utils import utc_now_naive


class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    part = Column(String(50), nullable=False)  # "C_programming" | "data_structure"
    chapter = Column(String(20), default="")   # "1.1"
    order = Column(Integer, default=0)
    difficulty = Column(Integer, default=3)
    exam_weight = Column(String(20), default="中频")  # "高频" | "中频" | "低频"
    ai_explanation = Column(Text, default="")
    created_at = Column(DateTime, default=utc_now_naive)

    parent = relationship("KnowledgePoint", remote_side=[id], back_populates="children")
    children = relationship("KnowledgePoint", back_populates="parent", lazy="selectin")
    questions = relationship("QuestionKnowledgePoint", back_populates="knowledge_point", lazy="selectin")
    mastery = relationship("KnowledgeMastery", back_populates="knowledge_point", uselist=False, lazy="selectin")
