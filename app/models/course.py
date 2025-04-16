from sqlalchemy import Column, String, Text, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.associations import user_course_association
class Course(Base):
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)

    category = Column(String, nullable=True)
    difficulty_level = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    is_published = Column(Boolean, default=False)

    owner_id = Column(String, ForeignKey("user.id"))
    instructor_id = Column(String, ForeignKey("user.id"), nullable=False)
    tags = Column(Text, nullable=True)
    owner = relationship("User", back_populates="owned_courses", foreign_keys=[owner_id])
    instructor = relationship("User", back_populates="instructed_courses", foreign_keys=[instructor_id])

    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    tests = relationship("Test", back_populates="course", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="course")

    students = relationship(
        "User",
        secondary=user_course_association,
        back_populates="enrolled_courses"
    )