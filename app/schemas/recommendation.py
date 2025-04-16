from typing import Optional
from pydantic import BaseModel


class CourseRecommendation(BaseModel):
    id: str
    course_id: str
    title: str
    reason: Optional[str] = None
    score: float


class LessonRecommendation(BaseModel):
    id: str
    lesson_id: str
    title: str
    reason: Optional[str] = None
    score: float


class UserBasedRecommendation(BaseModel):
    id: str
    item_id: str
    item_type: str  # e.g., "course", "lesson"
    title: Optional[str]
    reason: Optional[str]
    score: float

class RecommendationBase(BaseModel):
    user_id: str
    item_id: str
    item_type: str  # e.g. "course" or "lesson"
    reason: Optional[str] = None
    score: float


class RecommendationCreate(RecommendationBase):
    pass


class RecommendationUpdate(BaseModel):
    reason: Optional[str] = None
    score: Optional[float] = None


class RecommendationOut(RecommendationBase):
    id: str

    class Config:
        orm_mode = True

Recommendation = RecommendationOut
