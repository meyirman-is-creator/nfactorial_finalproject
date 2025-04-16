import uuid
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.test import Test
from app.schemas.test import TestCreate, TestUpdate


class CRUDTest(CRUDBase[Test, TestCreate, TestUpdate]):
    def create(self, db: Session, *, obj_in: TestCreate) -> Test:
        """
        Create new test.
        """
        test_id = str(uuid.uuid4())
        db_obj = Test(
            id=test_id,
            title=obj_in.title,
            description=obj_in.description,
            lesson_id=obj_in.lesson_id,
            time_limit_minutes=obj_in.time_limit_minutes,
            pass_score=obj_in.pass_score,
            max_attempts=obj_in.max_attempts,
            is_published=obj_in.is_published,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_lesson(
            self, db: Session, *, lesson_id: str, skip: int = 0, limit: int = 100
    ) -> List[Test]:
        """
        Get tests by lesson.
        """
        return (
            db.query(Test)
            .filter(Test.lesson_id == lesson_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_course(
            self, db: Session, *, course_id: str, skip: int = 0, limit: int = 100
    ) -> List[Test]:
        """
        Get tests by course.
        """
        from app.models.lesson import Lesson

        return (
            db.query(Test)
            .join(Lesson, Test.lesson_id == Lesson.id)
            .filter(Lesson.course_id == course_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_user(
            self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[Test]:
        """
        Get tests that user has access to.
        """
        from app.models.user import User
        from app.models.lesson import Lesson

        # Get courses the user is enrolled in
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []

        # This assumes there's a many-to-many relationship between users and enrolled_courses
        course_ids = [course.id for course in user.enrolled_courses]

        return (
            db.query(Test)
            .join(Lesson, Test.lesson_id == Lesson.id)
            .filter(
                Lesson.course_id.in_(course_ids),
                Test.is_published == True
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def add_question(
            self, db: Session, *, test_id: str, question_data: Dict[str, Any]
    ) -> Test:
        """
        Add a question to a test.
        """
        from app.models.question import Question

        test_obj = self.get(db=db, id=test_id)
        if not test_obj:
            return None

        question_id = str(uuid.uuid4())

        # Create question object
        question = Question(
            id=question_id,
            test_id=test_id,
            text=question_data.get("text"),
            question_type=question_data.get("question_type"),
            points=question_data.get("points", 1),
            options=question_data.get("options", []),
            correct_answer=question_data.get("correct_answer"),
            explanation=question_data.get("explanation")
        )

        db.add(question)
        db.commit()

        # Return test with questions
        return self.get_test_with_questions(db=db, test_id=test_id)

    def get_test_with_questions(
            self, db: Session, *, test_id: str
    ) -> Dict[str, Any]:
        """
        Get test with all questions.
        """
        from app.models.question import Question

        test_obj = self.get(db=db, id=test_id)
        if not test_obj:
            return None

        questions = (
            db.query(Question)
            .filter(Question.test_id == test_id)
            .all()
        )

        # Convert to dict to add questions
        test_dict = {
            "id": test_obj.id,
            "title": test_obj.title,
            "description": test_obj.description,
            "lesson_id": test_obj.lesson_id,
            "time_limit_minutes": test_obj.time_limit_minutes,
            "pass_score": test_obj.pass_score,
            "max_attempts": test_obj.max_attempts,
            "is_published": test_obj.is_published,
            "questions": [
                {
                    "id": q.id,
                    "text": q.text,
                    "question_type": q.question_type,
                    "points": q.points,
                    "options": q.options,
                    # Only include correct answer for admin or when viewing test results
                    # "correct_answer": q.correct_answer,
                    # "explanation": q.explanation
                } for q in questions
            ]
        }

        return test_dict


test = CRUDTest(Test)