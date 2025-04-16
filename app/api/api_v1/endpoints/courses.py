from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.course import Course
from app.crud.course import course
from app.schemas.course import Course as CourseSchema, CourseCreate, CourseUpdate
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any

from app import crud
from app import models
from app import schemas
from app.api.deps import get_db, get_current_active_user



router = APIRouter()


@router.get("/", response_model=List[CourseSchema])
def read_courses(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve courses.
    """
    if current_user.role == "admin":
        courses = course.get_multi(db, skip=skip, limit=limit)
    else:
        courses = course.get_multi_by_user(
            db=db, user_id=current_user.id, skip=skip, limit=limit
        )
    return courses


@router.post("/", response_model=CourseSchema)
def create_course(
        *,
        db: Session = Depends(get_db),
        course_in: CourseCreate,
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Create new course.
    """
    course_obj = course.create(db=db, obj_in=course_in)
    return course_obj


@router.get("/{course_id}", response_model=CourseSchema)
def read_course(
        *,
        db: Session = Depends(get_db),
        course_id: str,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get course by ID.
    """
    course_obj = course.get(db=db, id=course_id)
    if not course_obj:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if user has access to this course
    if current_user.role != "admin" and not course.is_user_enrolled(
            db=db, user_id=current_user.id, course_id=course_id
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return course_obj


@router.put("/{course_id}", response_model=CourseSchema)
def update_course(
        *,
        db: Session = Depends(get_db),
        course_id: str,
        course_in: CourseUpdate,
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Update a course.
    """
    course_obj = course.get(db=db, id=course_id)
    if not course_obj:
        raise HTTPException(status_code=404, detail="Course not found")

    course_obj = course.update(db=db, db_obj=course_obj, obj_in=course_in)
    return course_obj


@router.delete("/{course_id}", response_model=CourseSchema)
def delete_course(
        *,
        db: Session = Depends(get_db),
        course_id: str,
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Delete a course.
    """
    course_obj = course.get(db=db, id=course_id)
    if not course_obj:
        raise HTTPException(status_code=404, detail="Course not found")

    course_obj = course.remove(db=db, id=course_id)
    return course_obj


@router.post("/{course_id}/enroll", response_model=CourseSchema)
def enroll_in_course(
    *,
    db: Session = Depends(get_db),
    course_id: str,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Enroll current user in a course.
    """
    course_obj = course.get(db=db, id=course_id)
    if not course_obj:
        raise HTTPException(status_code=404, detail="Course not found")

    if current_user in course_obj.students:
        raise HTTPException(status_code=400, detail="User already enrolled in this course")

    course_obj.students.append(current_user)
    db.commit()
    db.refresh(course_obj)
    return course_obj