import uuid
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.submission import Submission
from app.schemas.submission import SubmissionCreate, SubmissionUpdate


class CRUDSubmission(CRUDBase[Submission, SubmissionCreate, SubmissionUpdate]):
    def create(self, db: Session, *, obj_in: SubmissionCreate, user_id: str) -> Submission:
        """
        Create new submission.
        """
        submission_id = str(uuid.uuid4())
        db_obj = Submission(
            id=submission_id,
            assignment_id=obj_in.assignment_id,
            user_id=user_id,
            content=obj_in.content,
            submitted_at=obj_in.submitted_at,
            points_awarded=None,
            feedback=None,
            status="submitted",
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_assignment(
            self, db: Session, *, assignment_id: str, skip: int = 0, limit: int = 100
    ) -> List[Submission]:
        """
        Get submissions by assignment.
        """
        return (
            db.query(Submission)
            .filter(Submission.assignment_id == assignment_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_user(
            self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[Submission]:
        """
        Get submissions by user.
        """
        return (
            db.query(Submission)
            .filter(Submission.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_user_and_assignment(
            self, db: Session, *, user_id: str, assignment_id: str
    ) -> Optional[Submission]:
        """
        Get submission by user and assignment.
        """
        return (
            db.query(Submission)
            .filter(
                Submission.user_id == user_id,
                Submission.assignment_id == assignment_id
            )
            .first()
        )

    def grade_submission(
            self, db: Session, *, submission_id: str, points_awarded: float, feedback: str
    ) -> Submission:
        """
        Grade a submission.
        """
        submission = self.get(db=db, id=submission_id)
        if not submission:
            return None

        submission.points_awarded = points_awarded
        submission.feedback = feedback
        submission.status = "graded"

        db.add(submission)
        db.commit()
        db.refresh(submission)
        return submission

    def get_ungraded_submissions(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Submission]:
        """
        Get all ungraded submissions.
        """
        return (
            db.query(Submission)
            .filter(Submission.status == "submitted")
            .offset(skip)
            .limit(limit)
            .all()
        )


submission = CRUDSubmission(Submission)