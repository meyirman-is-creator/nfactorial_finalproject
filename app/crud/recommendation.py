import uuid
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.recommendation import Recommendation
from app.schemas.recommendation import RecommendationCreate, RecommendationUpdate
from app.services.recommendation_service import RecommendationService



class CRUDRecommendation(CRUDBase[Recommendation, RecommendationCreate, RecommendationUpdate]):
    def create(self, db: Session, *, obj_in: RecommendationCreate) -> Recommendation:
        """
        Create new recommendation.
        """
        recommendation_id = str(uuid.uuid4())
        db_obj = Recommendation(
            id=recommendation_id,
            user_id=obj_in.user_id,
            item_id=obj_in.item_id,
            item_type=obj_in.item_type,
            reason=obj_in.reason,
            score=obj_in.score,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_user(
            self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[Recommendation]:
        """
        Get recommendations by user.
        """
        return (
            db.query(Recommendation)
            .filter(Recommendation.user_id == user_id)
            .order_by(Recommendation.score.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_recommended_courses(
            self, db: Session, *, user_id: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get personalized course recommendations based on user's history and preferences.
        """
        from app.models.course import Course
        from app.services.recommendation_service import RecommendationService

        # In a real application, this would call a more sophisticated recommendation engine
        # For now, we'll simulate this by getting recommendations from database or generating new ones

        # Check if we have stored recommendations
        stored_recommendations = (
            db.query(Recommendation)
            .filter(
                Recommendation.user_id == user_id,
                Recommendation.item_type == "course"
            )
            .order_by(Recommendation.score.desc())
            .limit(limit)
            .all()
        )

        if stored_recommendations:
            # Format and return stored recommendations
            result = []
            for rec in stored_recommendations:
                course = db.query(Course).filter(Course.id == rec.item_id).first()
                if course:
                    result.append({
                        "id": rec.id,
                        "course_id": course.id,
                        "title": course.title,
                        "reason": rec.reason,
                        "score": rec.score
                    })
            return result
        else:
            # Generate new recommendations
            return generate_course_recommendations(db, user_id=user_id, limit=limit)

    def get_recommended_lessons(
            self, db: Session, *, user_id: str, course_id: str, limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get recommended lessons within a course based on user's progress.
        """
        from app.models.lesson import Lesson
        from app.services.recommendation_service import generate_lesson_recommendations

        # Similar to course recommendations but filtered by course
        stored_recommendations = (
            db.query(Recommendation)
            .join(Lesson, Recommendation.item_id == Lesson.id)
            .filter(
                Recommendation.user_id == user_id,
                Recommendation.item_type == "lesson",
                Lesson.course_id == course_id
            )
            .order_by(Recommendation.score.desc())
            .limit(limit)
            .all()
        )

        if stored_recommendations:
            # Format and return stored recommendations
            result = []
            for rec in stored_recommendations:
                lesson = db.query(Lesson).filter(Lesson.id == rec.item_id).first()
                if lesson:
                    result.append({
                        "id": rec.id,
                        "lesson_id": lesson.id,
                        "title": lesson.title,
                        "reason": rec.reason,
                        "score": rec.score
                    })
            return result
        else:
            # Generate new recommendations
            return generate_lesson_recommendations(db, user_id=user_id, course_id=course_id, limit=limit)

    def get_similar_users_recommendations(
            self, db: Session, *, user_id: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations based on similar users' activities.
        """
        from app.services.recommendation_service import generate_similar_users_recommendations

        # This would typically use collaborative filtering
        return generate_similar_users_recommendations(db, user_id=user_id, limit=limit)

    def get_user_next_steps(
            self, db: Session, *, user_id: str, limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get personalized next learning steps for the user.
        Could be a mix of lessons, courses, or recommendations.
        """
        from app.services.recommendation_service import generate_next_steps

        # Try to fetch from existing stored recommendations
        stored = (
            db.query(Recommendation)
            .filter(Recommendation.user_id == user_id)
            .order_by(Recommendation.score.desc())
            .limit(limit)
            .all()
        )

        results = []
        for rec in stored:
            item = {"id": rec.id, "type": rec.item_type, "score": rec.score, "reason": rec.reason}
            if rec.item_type == "course":
                from app.models.course import Course
                course = db.query(Course).filter(Course.id == rec.item_id).first()
                if course:
                    item["title"] = course.title
                    item["item_id"] = course.id
            elif rec.item_type == "lesson":
                from app.models.lesson import Lesson
                lesson = db.query(Lesson).filter(Lesson.id == rec.item_id).first()
                if lesson:
                    item["title"] = lesson.title
                    item["item_id"] = lesson.id
            results.append(item)

        if results:
            return results

        # Fallback to generating recommendations dynamically
        return generate_next_steps(db=db, user_id=user_id, limit=limit)

recommendation = CRUDRecommendation(Recommendation)
