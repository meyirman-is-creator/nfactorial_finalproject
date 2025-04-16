from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.crud.recommendation import recommendation
from app.crud.course import course
from app.schemas.recommendation import CourseRecommendation, LessonRecommendation, UserBasedRecommendation
from app.services.recommendation_service import RecommendationService

router = APIRouter()


@router.get("/courses")
def get_course_recommendations(
    db: Session = Depends(get_db),
    limit: int = 5,
    current_user: User = Depends(get_current_active_user),
):
    user_id = current_user.id
    recommended_courses = RecommendationService.get_recommendations(db, user_id, limit)
    return recommended_courses

@router.get("/lessons/{course_id}", response_model=List[LessonRecommendation])
def get_lesson_recommendations(
        *,
        db: Session = Depends(get_db),
        course_id: str,
        limit: int = Query(3, ge=1, le=10),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get recommended lessons within a course based on user's progress.
    """
    # Check if user has access to this course
    if not course.is_user_enrolled(db=db, user_id=current_user.id, course_id=course_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    recommended_lessons = recommendation.get_recommended_lessons(
        db=db,
        user_id=current_user.id,
        course_id=course_id,
        limit=limit
    )
    return recommended_lessons


@router.get("/similar-users", response_model=List[UserBasedRecommendation])
def get_similar_users_recommendations(
        *,
        db: Session = Depends(get_db),
        limit: int = Query(5, ge=1, le=20),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get recommendations based on similar users' activities.
    """
    user_based_recommendations = recommendation.get_similar_users_recommendations(
        db=db,
        user_id=current_user.id,
        limit=limit
    )
    return user_based_recommendations


@router.get("/next-steps", response_model=List[LessonRecommendation])
def get_next_steps(
        *,
        db: Session = Depends(get_db),
        limit: int = Query(3, ge=1, le=10),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get personalized next steps for the user across all enrolled courses.
    """
    next_steps = recommendation.get_user_next_steps(
        db=db,
        user_id=current_user.id,
        limit=limit
    )
    return next_steps


@router.post("/feedback/{recommendation_id}", response_model=bool)
def submit_recommendation_feedback(
        *,
        db: Session = Depends(get_db),
        recommendation_id: str,
        is_helpful: bool,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Submit feedback for a recommendation to improve future recommendations.
    """
    success = recommendation.record_feedback(
        db=db,
        recommendation_id=recommendation_id,
        user_id=current_user.id,
        is_helpful=is_helpful
    )
    return success