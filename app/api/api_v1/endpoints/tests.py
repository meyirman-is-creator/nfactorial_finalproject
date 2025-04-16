from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.test import Test
from app.crud.test import test
from app.crud.course import course
from app.crud.lesson import lesson
from app.schemas.test import Test as TestSchema, TestCreate, TestUpdate, TestWithQuestions

router = APIRouter()


@router.get("/", response_model=List[TestSchema])
def read_tests(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        lesson_id: str = None,
        course_id: str = None,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve tests.
    """
    if lesson_id:
        lesson_obj = lesson.get(db=db, id=lesson_id)
        if not lesson_obj:
            raise HTTPException(status_code=404, detail="Lesson not found")

        # Check if user has access to this lesson's course
        if current_user.role != "admin" and not course.is_user_enrolled(
                db=db, user_id=current_user.id, course_id=lesson_obj.course_id
        ):
            raise HTTPException(status_code=403, detail="Not enough permissions")

        tests = test.get_multi_by_lesson(
            db=db, lesson_id=lesson_id, skip=skip, limit=limit
        )
    elif course_id:
        # Check if user has access to this course
        if current_user.role != "admin" and not course.is_user_enrolled(
                db=db, user_id=current_user.id, course_id=course_id
        ):
            raise HTTPException(status_code=403, detail="Not enough permissions")

        tests = test.get_multi_by_course(
            db=db, course_id=course_id, skip=skip, limit=limit
        )
    elif current_user.role == "admin":
        tests = test.get_multi(db=db, skip=skip, limit=limit)
    else:
        tests = test.get_multi_by_user(
            db=db, user_id=current_user.id, skip=skip, limit=limit
        )
    return tests


@router.post("/", response_model=TestSchema)
def create_test(
        *,
        db: Session = Depends(get_db),
        test_in: TestCreate,
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Create new test.
    """
    # Check if lesson exists
    lesson_obj = lesson.get(db=db, id=test_in.lesson_id)
    if not lesson_obj:
        raise HTTPException(status_code=404, detail="Lesson not found")

    test_obj = test.create(db=db, obj_in=test_in)
    return test_obj


@router.get("/{test_id}", response_model=TestWithQuestions)
def read_test(
        *,
        db: Session = Depends(get_db),
        test_id: str,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get test by ID with all questions.
    """
    test_obj = test.get(db=db, id=test_id)
    if not test_obj:
        raise HTTPException(status_code=404, detail="Test not found")

    # Get lesson and course info
    lesson_obj = lesson.get(db=db, id=test_obj.lesson_id)

    # Check if user has access to this test's course
    if current_user.role != "admin" and not course.is_user_enrolled(
            db=db, user_id=current_user.id, course_id=lesson_obj.course_id
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Get test with questions
    return test.get_test_with_questions(db=db, test_id=test_id)


@router.put("/{test_id}", response_model=TestSchema)
def update_test(
        *,
        db: Session = Depends(get_db),
        test_id: str,
        test_in: TestUpdate,
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Update a test.
    """
    test_obj = test.get(db=db, id=test_id)
    if not test_obj:
        raise HTTPException(status_code=404, detail="Test not found")

    test_obj = test.update(db=db, db_obj=test_obj, obj_in=test_in)
    return test_obj


@router.delete("/{test_id}", response_model=TestSchema)
def delete_test(
        *,
        db: Session = Depends(get_db),
        test_id: str,
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Delete a test.
    """
    test_obj = test.get(db=db, id=test_id)
    if not test_obj:
        raise HTTPException(status_code=404, detail="Test not found")

    test_obj = test.remove(db=db, id=test_id)
    return test_obj


@router.post("/{test_id}/add-question", response_model=TestWithQuestions)
def add_question_to_test(
        *,
        db: Session = Depends(get_db),
        test_id: str,
        question_data: dict = Body(...),
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Add a question to a test.
    """
    test_obj = test.get(db=db, id=test_id)
    if not test_obj:
        raise HTTPException(status_code=404, detail="Test not found")

    updated_test = test.add_question(db=db, test_id=test_id, question_data=question_data)
    return updated_test