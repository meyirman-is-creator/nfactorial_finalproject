import uuid
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.test_result import TestResult
from app.schemas.test_result import TestResultCreate, TestResultUpdate


class CRUDTestResult(CRUDBase[TestResult, TestResultCreate, TestResultUpdate]):
    def create(self, db: Session, *, obj_in: TestResultCreate, user_id: str) -> TestResult:
        """
        Create new test result.
        """
        result_id = str(uuid.uuid4())
        db_obj = TestResult(
            id=result_id,
            test_id=obj_in.test_id,
            user_id=user_id,
            score=obj_in.score,
            passed=obj_in.passed,
            answers=obj_in.answers,
            completed_at=obj_in.completed_at,
            time_taken_seconds=obj_in.time_taken_seconds,
            attempt_number=obj_in.attempt_number,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_test(
            self, db: Session, *, test_id: str, skip: int = 0, limit: int = 100
    ) -> List[TestResult]:
        """
        Get results by test.
        """
        return (
            db.query(TestResult)
            .filter(TestResult.test_id == test_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_user(
            self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[TestResult]:
        """
        Get results by user.
        """
        return (
            db.query(TestResult)
            .filter(TestResult.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_user_and_test(
            self, db: Session, *, user_id: str, test_id: str
    ) -> List[TestResult]:
        """
        Get all attempts for a user on a specific test.
        """
        return (
            db.query(TestResult)
            .filter(
                TestResult.user_id == user_id,
                TestResult.test_id == test_id
            )
            .order_by(TestResult.attempt_number)
            .all()
        )

    def get_best_result(
            self, db: Session, *, user_id: str, test_id: str
    ) -> Optional[TestResult]:
        """
        Get the best result (highest score) for a user on a test.
        """
        return (
            db.query(TestResult)
            .filter(
                TestResult.user_id == user_id,
                TestResult.test_id == test_id
            )
            .order_by(TestResult.score.desc())
            .first()
        )

    def get_latest_result(
            self, db: Session, *, user_id: str, test_id: str
    ) -> Optional[TestResult]:
        """
        Get the latest result for a user on a test.
        """
        return (
            db.query(TestResult)
            .filter(
                TestResult.user_id == user_id,
                TestResult.test_id == test_id
            )
            .order_by(TestResult.completed_at.desc())
            .first()
        )

    def count_attempts(
            self, db: Session, *, user_id: str, test_id: str
    ) -> int:
        """
        Count how many attempts a user has made on a test.
        """
        return (
            db.query(TestResult)
            .filter(
                TestResult.user_id == user_id,
                TestResult.test_id == test_id
            )
            .count()
        )

    def calculate_average_score(
            self, db: Session, *, test_id: str
    ) -> float:
        """
        Calculate the average score for a test across all users.
        """
        from sqlalchemy import func

        result = (
            db.query(func.avg(TestResult.score))
            .filter(TestResult.test_id == test_id)
            .scalar()
        )

        return float(result) if result is not None else 0.0


test_result = CRUDTestResult(TestResult)