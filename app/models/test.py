from sqlalchemy import Column, String, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Test(Base):
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    questions = Column(JSON)  # JSON array of questions
    course_id = Column(String, ForeignKey("course.id"))

    # Relationships
    course = relationship("Course", back_populates="tests")
    results = relationship("TestResult", back_populates="test", cascade="all, delete-orphan")