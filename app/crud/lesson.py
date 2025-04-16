import uuid
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.lesson import Lesson
from app.schemas.lesson import LessonCreate, LessonUpdate


class CRUDLesson(CRUDBase[Lesson, LessonCreate, LessonUpdate]):
    def create(self, db: Session, *, obj_in: LessonCreate) -> Lesson:
        """
        Create new lesson.
        """
        lesson_id = str(uuid.uuid4())
        db_obj = Lesson(
            id=lesson_id,
            title=obj_in.title,
            content=obj_in.content,
            course_id=obj_in.course_id,
            order=obj_in.order,
            duration_minutes=obj_in.duration_minutes,
            is_published=obj_in.is_published,
            video_url=obj_in.video_url,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_course(
            self, db: Session, *, course_id: str, skip: int = 0, limit: int = 100
    ) -> List[Lesson]:
        """
        Get lessons by course.
        """
        return (
            db.query(Lesson)
            .filter(Lesson.course_id == course_id)
            .order_by(Lesson.order)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_published_lessons(
            self, db: Session, *, course_id: str, skip: int = 0, limit: int = 100
    ) -> List[Lesson]:
        """
        Get published lessons for a course.
        """
        return (
            db.query(Lesson)
            .filter(Lesson.course_id == course_id, Lesson.is_published == True)
            .order_by(Lesson.order)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_lesson_order(
            self, db: Session, *, lesson_id: str, new_order: int
    ) -> Lesson:
        """
        Update a lesson's order.
        """
        lesson = self.get(db=db, id=lesson_id)
        if not lesson:
            return None

        lesson.order = new_order
        db.add(lesson)
        db.commit()
        db.refresh(lesson)
        return lesson

    def mark_lesson_completed(
            self, db: Session, *, lesson_id: str, user_id: str
    ) -> bool:
        """
        Mark a lesson as completed by a user.
        """
        from app.models.user import User

        lesson = self.get(db=db, id=lesson_id)
        user = db.query(User).filter(User.id == user_id).first()

        if not lesson or not user:
            return False

        # This assumes there's a many-to-many relationship between users and completed_lessons
        if lesson not in user.completed_lessons:
            user.completed_lessons.append(lesson)
            db.commit()

        return True

    def is_lesson_completed(
            self, db: Session, *, lesson_id: str, user_id: str
    ) -> bool:
        """
        Check if a lesson has been completed by a user.
        """
        from app.models.user import User

        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            return False

        # This assumes there's a many-to-many relationship between users and completed_lessons
        return any(lesson.id == lesson_id for lesson in user.completed_lessons)


lesson = CRUDLesson(Lesson)