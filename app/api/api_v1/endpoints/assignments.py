from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.assignment import Assignment
from app.crud.assignment import assignment
from app.crud.course import course
from app.crud.lesson import lesson
from app.schemas.assignment import Assignment as AssignmentSchema, AssignmentCreate, AssignmentUpdate

router = APIRouter()


@router.get("/", response_model=List[AssignmentSchema])
def read_assignments(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        lesson_id: str = None,
        course_id: str = None,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve assignments.
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

        assignments = assignment.get_multi_by_lesson(
            db=db, lesson_id=lesson_id, skip=skip, limit=limit
        )
    elif course_id:
        # Check if user has access to this course
        if current_user.role != "admin" and not course.is_user_enrolled(
                db=db, user_id=current_user.id, course_id=course_id
        ):
            raise HTTPException(status_code=403, detail="Not enough permissions")

        assignments = assignment.get_multi_by_course(
            db=db, course_id=course_id, skip=skip, limit=limit
        )
    elif current_user.role == "admin":
        assignments = assignment.get_multi(db=db, skip=skip, limit=limit)
    else:
        assignments = assignment.get_multi_by_user(
            db=db, user_id=current_user.id, skip=skip, limit=limit
        )
    return assignments


@router.post("/", response_model=AssignmentSchema)
def create_assignment(
        *,
        db: Session = Depends(get_db),
        assignment_in: AssignmentCreate,
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Create new assignment.
    """
    # Check if lesson exists
    lesson_obj = lesson.get(db=db, id=assignment_in.lesson_id)
    if not lesson_obj:
        raise HTTPException(status_code=404, detail="Lesson not found")

    assignment_obj = assignment.create(db=db, obj_in=assignment_in)
    return assignment_obj


@router.get("/{assignment_id}", response_model=AssignmentSchema)
def read_assignment(
        *,
        db: Session = Depends(get_db),
        assignment_id: str,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get assignment by ID.
    """
    assignment_obj = assignment.get(db=db, id=assignment_id)
    if not assignment_obj:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Get lesson and course info
    lesson_obj = lesson.get(db=db, id=assignment_obj.lesson_id)

    # Check if user has access to this assignment's course
    if current_user.role != "admin" and not course.is_user_enrolled(
            db=db, user_id=current_user.id, course_id=lesson_obj.course_id
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return assignment_obj


@router.put("/{assignment_id}", response_model=AssignmentSchema)
def update_assignment(
        *,
        db: Session = Depends(get_db),
        assignment_id: str,
        assignment_in: AssignmentUpdate,
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Update an assignment.
    """
    assignment_obj = assignment.get(db=db, id=assignment_id)
    if not assignment_obj:
        raise HTTPException(status_code=404, detail="Assignment not found")

    assignment_obj = assignment.update(db=db, db_obj=assignment_obj, obj_in=assignment_in)
    return assignment_obj


@router.delete("/{assignment_id}", response_model=AssignmentSchema)
def delete_assignment(
        *,
        db: Session = Depends(get_db),
        assignment_id: str,
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Delete an assignment.
    """
    assignment_obj = assignment.get(db=db, id=assignment_id)
    if not assignment_obj:
        raise HTTPException(status_code=404, detail="Assignment not found")

    assignment_obj = assignment.remove(db=db, id=assignment_id)
    return assignment_obj