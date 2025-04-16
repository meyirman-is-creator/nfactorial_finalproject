from sqlalchemy import Column, String, ForeignKey, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class TestResult(Base):
    id = Column(String, primary_key=True, index=True)
    score = Column(Float)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(String, ForeignKey("user.id"))
    test_id = Column(String, ForeignKey("test.id"))

    # Relationships
    user = relationship("User", back_populates="test_results")
    test = relationship("Test", back_populates="results")