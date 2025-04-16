from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, users, courses, lessons, assignments, submissions, tests, test_results, recommendations, chatbot

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["lessons"])
api_router.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
api_router.include_router(submissions.router, prefix="/submissions", tags=["submissions"])
api_router.include_router(tests.router, prefix="/tests", tags=["tests"])
api_router.include_router(test_results.router, prefix="/test-results", tags=["test-results"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])