from sqlalchemy import Column, String, Text, ForeignKey, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Submission(Base):
    id = Column(String, primary_key=True, index=True)
    content = Column(Text)
    grade = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    student_id = Column(String, ForeignKey("user.id"))
    assignment_id = Column(String, ForeignKey("assignment.id"))

    # Relationships
    student = relationship("User", back_populates="submissions")
    assignment = relationship("Assignment", back_populates="submissions")