from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.lesson import Lesson
from app.crud.lesson import lesson
from app.crud.course import course
from app.schemas.lesson import Lesson as LessonSchema, LessonCreate, LessonUpdate

router = APIRouter()


@router.get("/", response_model=List[LessonSchema])
def read_lessons(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        course_id: str = None,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve lessons.
    """
    if course_id:
        # Check if user has access to this course
        if current_user.role != "admin" and not course.is_user_enrolled(
                db=db, user_id=current_user.id, course_id=course_id
        ):
            raise HTTPException(status_code=403, detail="Not enough permissions")

        lessons = lesson.get_multi_by_course(
            db=db, course_id=course_id, skip=skip, limit=limit
        )
    elif current_user.role == "admin":
        lessons = lesson.get_multi(db=db, skip=skip, limit=limit)
    else:
        lessons = lesson.get_multi_by_user(
            db=db, user_id=current_user.id, skip=skip, limit=limit
        )
    return lessons


@router.post("/", response_model=LessonSchema)
def create_lesson(
        *,
        db: Session = Depends(get_db),
        lesson_in: LessonCreate,
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Create new lesson.
    """
    # Check if course exists
    course_obj = course.get(db=db, id=lesson_in.course_id)
    if not course_obj:
        raise HTTPException(status_code=404, detail="Course not found")

    lesson_obj = lesson.create(db=db, obj_in=lesson_in)
    return lesson_obj


@router.get("/{lesson_id}", response_model=LessonSchema)
def read_lesson(
        *,
        db: Session = Depends(get_db),
        lesson_id: str,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get lesson by ID.
    """
    lesson_obj = lesson.get(db=db, id=lesson_id)
    if not lesson_obj:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Check if user has access to this lesson's course
    if current_user.role != "admin" and not course.is_user_enrolled(
            db=db, user_id=current_user.id, course_id=lesson_obj.course_id
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return lesson_obj


@router.put("/{lesson_id}", response_model=LessonSchema)
def update_lesson(
        *,
        db: Session = Depends(get_db),
        lesson_id: str,
        lesson_in: LessonUpdate,
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Update a lesson.
    """
    lesson_obj = lesson.get(db=db, id=lesson_id)
    if not lesson_obj:
        raise HTTPException(status_code=404, detail="Lesson not found")

    lesson_obj = lesson.update(db=db, db_obj=lesson_obj, obj_in=lesson_in)
    return lesson_obj


@router.delete("/{lesson_id}", response_model=LessonSchema)
def delete_lesson(
        *,
        db: Session = Depends(get_db),
        lesson_id: str,
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Delete a lesson.
    """
    lesson_obj = lesson.get(db=db, id=lesson_id)
    if not lesson_obj:
        raise HTTPException(status_code=404, detail="Lesson not found")

    lesson_obj = lesson.remove(db=db, id=lesson_id)
    return lesson_obj


@router.post("/{lesson_id}/complete", response_model=LessonSchema)
def complete_lesson(
        *,
        db: Session = Depends(get_db),
        lesson_id: str,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Mark lesson as completed by current user.
    """
    lesson_obj = lesson.get(db=db, id=lesson_id)
    if not lesson_obj:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Check if user has access to this lesson's course
    if not course.is_user_enrolled(
            db=db, user_id=current_user.id, course_id=lesson_obj.course_id
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    lesson_obj = lesson.mark_completed(db=db, lesson_id=lesson_id, user_id=current_user.id)
    return lesson_obj