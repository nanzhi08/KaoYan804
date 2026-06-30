from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, ForeignKey
from ..database import Base
from ..time_utils import utc_now_naive


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    filename = Column(String(500), nullable=False)
    original_name = Column(String(500), nullable=False)
    file_type = Column(String(20), nullable=False)  # "pdf" | "docx" | "doc" | "md" | "txt" | "png" | "jpg" | "jpeg"
    file_size = Column(Integer, default=0)
    content_text = Column(Text, default="")
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=True)
    tags = Column(JSON, default=list)
    uploaded_at = Column(DateTime, default=utc_now_naive)
