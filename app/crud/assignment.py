import uuid
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.assignment import Assignment
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate


class CRUDAssignment(CRUDBase[Assignment, AssignmentCreate, AssignmentUpdate]):
    def create(self, db: Session, *, obj_in: AssignmentCreate) -> Assignment:
        """
        Create new assignment.
        """
        assignment_id = str(uuid.uuid4())
        db_obj = Assignment(
            id=assignment_id,
            title=obj_in.title,
            description=obj_in.description,
            lesson_id=obj_in.lesson_id,
            due_date=obj_in.due_date,
            max_points=obj_in.max_points,
            is_published=obj_in.is_published,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_lesson(
            self, db: Session, *, lesson_id: str, skip: int = 0, limit: int = 100
    ) -> List[Assignment]:
        """
        Get assignments by lesson.
        """
        return (
            db.query(Assignment)
            .filter(Assignment.lesson_id == lesson_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_course(
            self, db: Session, *, course_id: str, skip: int = 0, limit: int = 100
    ) -> List[Assignment]:
        """
        Get assignments by course.
        """
        from app.models.lesson import Lesson

        return (
            db.query(Assignment)
            .join(Lesson, Assignment.lesson_id == Lesson.id)
            .filter(Lesson.course_id == course_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_published_assignments(
            self, db: Session, *, lesson_id: str, skip: int = 0, limit: int = 100
    ) -> List[Assignment]:
        """
        Get published assignments for a lesson.
        """
        return (
            db.query(Assignment)
            .filter(Assignment.lesson_id == lesson_id, Assignment.is_published == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_assignments_due_soon(
            self, db: Session, *, user_id: str, days: int = 7, skip: int = 0, limit: int = 100
    ) -> List[Assignment]:
        """
        Get assignments due within specified number of days.
        """
        from app.models.user import User
        from app.models.lesson import Lesson
        import datetime

        # Get courses the user is enrolled in
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []

        due_date_cutoff = datetime.datetime.utcnow() + datetime.timedelta(days=days)

        # This assumes there's a many-to-many relationship between users and enrolled_courses
        course_ids = [course.id for course in user.enrolled_courses]

        return (
            db.query(Assignment)
            .join(Lesson, Assignment.lesson_id == Lesson.id)
            .filter(
                Lesson.course_id.in_(course_ids),
                Assignment.due_date <= due_date_cutoff,
                Assignment.is_published == True
            )
            .order_by(Assignment.due_date)
            .offset(skip)
            .limit(limit)
            .all()
        )


assignment = CRUDAssignment(Assignment)