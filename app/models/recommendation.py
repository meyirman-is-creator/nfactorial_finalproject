from sqlalchemy import Column, String, ForeignKey, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Recommendation(Base):
    id = Column(String, primary_key=True, index=True)
    score = Column(Float)  # Relevance score
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(String, ForeignKey("user.id"))
    course_id = Column(String, ForeignKey("course.id"))

    # Relationships
    user = relationship("User", back_populates="recommendations")
    course = relationship("Course", back_populates="recommendations")