from sqlalchemy import Column, String, Text, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Lesson(Base):
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    course_id = Column(String, ForeignKey("course.id"))

    order = Column(Integer, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    is_published = Column(Boolean, default=False)
    video_url = Column(String, nullable=True)

    # Relationships
    course = relationship("Course", back_populates="lessons")
    assignments = relationship("Assignment", back_populates="lesson", cascade="all, delete-orphan")
