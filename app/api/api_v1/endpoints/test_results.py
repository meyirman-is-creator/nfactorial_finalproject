from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.test_result import TestResult
from app.crud.test_result import test_result
from app.crud.test import test
from app.crud.course import course
from app.crud.lesson import lesson
from app.schemas.test_result import TestResultOut as TestResultSchema

router = APIRouter()


@router.get("/", response_model=List[TestResultSchema])
def read_test_results(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        test_id: str = None,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve test results.
    """
    if test_id:
        # Get test info
        test_obj = test.get(db=db, id=test_id)
        if not test_obj:
            raise HTTPException(status_code=404, detail="Test not found")

        lesson_obj = lesson.get(db=db, id=test_obj.lesson_id)

        # Admin can see all results, users can only see their own
        if current_user.role == "admin":
            results = test_result.get_multi_by_test(
                db=db, test_id=test_id, skip=skip, limit=limit
            )
        else:
            # Check if user has access to this course
            if not course.is_user_enrolled(
                    db=db, user_id=current_user.id, course_id=lesson_obj.course_id
            ):
                raise HTTPException(status_code=403, detail="Not enough permissions")

            # User can only see their own results
            results = test_result.get_