import uuid
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.course import Course
from app.models.user import User
from app.schemas.course import CourseCreate, CourseUpdate


class CRUDCourse(CRUDBase[Course, CourseCreate, CourseUpdate]):
    def get(self, db: Session, id: str) -> Optional[Course]:
        return db.query(Course).filter(Course.id == id).first()

    def create(self, db: Session, *, obj_in: CourseCreate) -> Course:
        """
        Create new course.
        """
        course_id = str(uuid.uuid4())
        db_obj = Course(
            id=course_id,
            title=obj_in.title,
            description=obj_in.description,
            instructor_id=obj_in.instructor_id,
            category=obj_in.category,
            is_published=obj_in.is_published,
            difficulty_level=obj_in.difficulty_level,
            price=obj_in.price,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_instructor(
            self, db: Session, *, instructor_id: str, skip: int = 0, limit: int = 100
    ) -> List[Course]:
        """
        Get courses by instructor.
        """
        return (
            db.query(Course)
            .filter(Course.instructor_id == instructor_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_category(
            self, db: Session, *, category: str, skip: int = 0, limit: int = 100
    ) -> List[Course]:
        """
        Get courses by category.
        """
        return (
            db.query(Course)
            .filter(Course.category == category)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_published_courses(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Course]:
        """
        Get all published courses.
        """
        return (
            db.query(Course)
            .filter(Course.is_published == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def is_user_enrolled(self, db: Session, *, user_id: str, course_id: str) -> bool:
        """
        Check if user is enrolled in the course.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        # This assumes there's a many-to-many relationship between users and courses
        return any(course.id == course_id for course in user.enrolled_courses)

    def enroll_user(self, db: Session, *, user_id: str, course_id: str) -> bool:
        """
        Enroll user in a course.
        """
        user = db.query(User).filter(User.id == user_id).first()
        course = db.query(Course).filter(Course.id == course_id).first()

        if not user or not course:
            return False

        # This assumes there's a many-to-many relationship between users and courses
        if course not in user.enrolled_courses:
            user.enrolled_courses.append(course)
            db.commit()

        return True

    def unenroll_user(self, db: Session, *, user_id: str, course_id: str) -> bool:
        """
        Unenroll user from a course.
        """
        user = db.query(User).filter(User.id == user_id).first()
        course = db.query(Course).filter(Course.id == course_id).first()

        if not user or not course:
            return False

        # This assumes there's a many-to-many relationship between users and courses
        if course in user.enrolled_courses:
            user.enrolled_courses.remove(course)
            db.commit()

        return True


course = CRUDCourse(Course)