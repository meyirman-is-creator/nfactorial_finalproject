import numpy as np
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.test import Test
from app.models.user import User
from app.models.course import Course
from app.models.test_result import TestResult
from app.models.recommendation import Recommendation


class RecommendationService:
    @staticmethod
    def get_recommendations(db: Session, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Generate course recommendations for a user.

        Args:
            db: Database session
            user_id: ID of the user to get recommendations for
            limit: Maximum number of recommendations to return

        Returns:
            List of recommended courses with relevance scores
        """
        # Get user's completed tests
        user_tests = db.query(TestResult).filter(TestResult.user_id == user_id).all()

        if not user_tests:
            # If user has no test results, recommend popular courses
            return RecommendationService.get_popular_courses(db, limit)

        # Get user's strengths based on test results
        strengths = {}
        for test_result in user_tests:
            test = db.query(Test).filter(Test.id == test_result.test_id).first()
            if test and test.course_id:
                course = db.query(Course).filter(Course.id == test.course_id).first()
                if course:
                    # Use course title as a simple category for now
                    if course.title not in strengths:
                        strengths[course.title] = []
                    strengths[course.title].append(test_result.score)

        # Calculate average score for each category
        for category, scores in strengths.items():
            strengths[category] = sum(scores) / len(scores)

        # Get all courses
        all_courses = db.query(Course).all()

        # Calculate relevance scores
        recommendations = []
        for course in all_courses:
            # Skip courses the user has already taken
            if course.title in strengths:
                continue

            # Calculate simple relevance score based on category matching
            # (In a real system, this would be more sophisticated)
            relevance_score = 0.5  # Base score
            for category, score in strengths.items():
                if category.lower() in course.title.lower() or course.title.lower() in category.lower():
                    relevance_score += 0.3 * score

            recommendations.append({
                "course": course,
                "score": relevance_score
            })

        # Sort by relevance score and limit results
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:limit]

    @staticmethod
    def get_popular_courses(db: Session, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get popular courses based on number of tests taken.

        Args:
            db: Database session
            limit: Maximum number of courses to return

        Returns:
            List of popular courses with default relevance scores
        """
        # Get courses with the most tests taken
        courses = db.query(Course).all()

        # Count number of test results for each course
        course_popularity = {}
        for course in courses:
            tests = db.query(Test).filter(Test.course_id == course.id).all()
            test_count = 0
            for test in tests:
                test_count += db.query(TestResult).filter(TestResult.test_id == test.id).count()
            course_popularity[course.id] = test_count

        # Sort courses by popularity
        sorted_courses = sorted(
            courses,
            key=lambda course: course_popularity.get(course.id, 0),
            reverse=True
        )

        # Return popular courses with default relevance scores
        recommendations = []
        for course in sorted_courses[:limit]:
            recommendations.append({
                "course": course,
                "score": 0.5  # Default score for popular courses
            })

        return recommendations

    @staticmethod
    def save_recommendations(db: Session, user_id: str, recommendations: List[Dict[str, Any]]) -> List[Recommendation]:
        """
        Save course recommendations to the database.

        Args:
            db: Database session
            user_id: ID of the user to save recommendations for
            recommendations: List of recommended courses with scores

        Returns:
            List of saved Recommendation objects
        """
        # Remove existing recommendations for this user
        db.query(Recommendation).filter(Recommendation.user_id == user_id).delete()

        # Create new recommendations
        saved_recommendations = []
        for rec in recommendations:
            recommendation = Recommendation(
                id=str(uuid.uuid4()),
                user_id=user_id,
                course_id=rec["course"].id,
                score=rec["score"]
            )
            db.add(recommendation)
            saved_recommendations.append(recommendation)

        db.commit()
        for rec in saved_recommendations:
            db.refresh(rec)

        return saved_recommendations