from sqlalchemy import Boolean, Column, String, Enum, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.course import Course
from app.models.associations import user_course_association


class User(Base):
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum("student", "teacher", "admin", name="user_role"), default="student")
    is_active = Column(Boolean(), default=True)

    owned_courses = relationship(
        "Course",
        back_populates="owner",
        foreign_keys="Course.owner_id"
    )

    instructed_courses = relationship(
        "Course",
        back_populates="instructor",
        foreign_keys="Course.instructor_id"
    )


    enrolled_courses = relationship(
        "Course",
        secondary=user_course_association,
        back_populates="students"
    )
    submissions = relationship("Submission", back_populates="student")
    test_results = relationship("TestResult", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")
