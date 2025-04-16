from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.submission import Submission
from app.crud.submission import submission
from app.crud.assignment import assignment
from app.crud.course import course
from app.crud.lesson import lesson
from app.schemas.submission import Submission as SubmissionSchema, SubmissionCreate, SubmissionUpdate

router = APIRouter()


@router.get("/", response_model=List[SubmissionSchema])
def read_submissions(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        assignment_id: str = None,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve submissions.
    """
    if assignment_id:
        # Get assignment and its lesson
        assignment_obj = assignment.get(db=db, id=assignment_id)
        if not assignment_obj:
            raise HTTPException(status_code=404, detail="Assignment not found")

        lesson_obj = lesson.get(db=db, id=assignment_obj.lesson_id)

        # Admin can see all submissions, users can only see their own
        if current_user.role == "admin":
            submissions = submission.get_multi_by_assignment(
                db=db, assignment_id=assignment_id, skip=skip, limit=limit
            )
        else:
            # Check if user has access to this course
            if not course.is_user_enrolled(
                    db=db, user_id=current_user.id, course_id=lesson_obj.course_id
            ):
                raise HTTPException(status_code=403, detail="Not enough permissions")

            # User can only see their own submissions
            submissions = submission.get_by_assignment_and_user(
                db=db, assignment_id=assignment_id, user_id=current_user.id
            )
    elif current_user.role == "admin":
        submissions = submission.get_multi(db=db, skip=skip, limit=limit)
    else:
        # Regular users can only see their own submissions
        submissions = submission.get_multi_by_user(
            db=db, user_id=current_user.id, skip=skip, limit=limit
        )
    return submissions


@router.post("/", response_model=SubmissionSchema)
def create_submission(
        *,
        db: Session = Depends(get_db),
        submission_in: SubmissionCreate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new submission.
    """
    # Check if assignment exists
    assignment_obj = assignment.get(db=db, id=submission_in.assignment_id)
    if not assignment_obj:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Get lesson for this assignment
    lesson_obj = lesson.get(db=db, id=assignment_obj.lesson_id)

    # Check if user has access to this course
    if not course.is_user_enrolled(
            db=db, user_id=current_user.id, course_id=lesson_obj.course_id
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Create submission with current user ID
    submission_data = submission_in.dict()
    submission_data["user_id"] = current_user.id

    submission_obj = submission.create(db=db, obj_in=submission_data)
    return submission_obj


@router.get("/{submission_id}", response_model=SubmissionSchema)
def read_submission(
        *,
        db: Session = Depends(get_db),
        submission_id: str,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get submission by ID.
    """
    submission_obj = submission.get(db=db, id=submission_id)
    if not submission_obj:
        raise HTTPException(status_code=404, detail="Submission not found")

    # Admin can see any submission, users can only see their own
    if current_user.role != "admin" and submission_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return submission_obj


@router.put("/{submission_id}", response_model=SubmissionSchema)
def update_submission(
        *,
        db: Session = Depends(get_db),
        submission_id: str,
        submission_in: SubmissionUpdate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a submission.
    """
    submission_obj = submission.get(db=db, id=submission_id)
    if not submission_obj:
        raise HTTPException(status_code=404, detail="Submission not found")

    # Only admin or the submission owner can update it
    if current_user.role != "admin" and submission_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Only admin can update grade and feedback
    if current_user.role != "admin" and (
            "grade" in submission_in.dict(exclude_unset=True) or
            "feedback" in submission_in.dict(exclude_unset=True)
    ):
        raise HTTPException(status_code=403, detail="Only instructors can update grades and feedback")

    submission_obj = submission.update(db=db, db_obj=submission_obj, obj_in=submission_in)
    return submission_obj


@router.delete("/{submission_id}", response_model=SubmissionSchema)
def delete_submission(
        *,
        db: Session = Depends(get_db),
        submission_id: str,
        current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Delete a submission.
    """
    submission_obj = submission.get(db=db, id=submission_id)
    if not submission_obj:
        raise HTTPException(status_code=404, detail="Submission not found")

    submission_obj = submission.remove(db=db, id=submission_id)
    return submission_obj