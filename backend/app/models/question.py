from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(30), nullable=False)
    # "single_choice" | "multi_choice" | "fill_blank" | "program_reading"
    # | "analysis" | "calculation" | "programming" | "short_answer"
    part = Column(String(50), nullable=False)  # "C_programming" | "data_structure"
    difficulty = Column(Integer, default=3)
    content = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)  # {"A":"...", "B":"...", "C":"...", "D":"..."}
    answer = Column(Text, nullable=False)
    explanation = Column(Text, default="")
    source = Column(String(200), nullable=True)
    code_snippet = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    knowledge_points = relationship("QuestionKnowledgePoint", back_populates="question", lazy="selectin")


class QuestionKnowledgePoint(Base):
    __tablename__ = "question_knowledge_points"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=False)

    question = relationship("Question", back_populates="knowledge_points")
    knowledge_point = relationship("KnowledgePoint", back_populates="questions")
