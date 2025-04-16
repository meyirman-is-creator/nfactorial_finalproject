import uuid
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


# Shared properties
class LessonBase(BaseModel):
    title: str
    content: str
    course_id: str


# Properties to receive via API on creation
class LessonCreate(BaseModel):
    title: str
    content: str
    course_id: str
    order: Optional[int] = None
    duration_minutes: Optional[int] = None
    is_published: Optional[bool] = False
    video_url: Optional[str] = None


# Properties to receive via API on update
class LessonUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    course_id: Optional[str] = None
    order: Optional[int] = None
    duration_minutes: Optional[int] = None
    is_published: Optional[bool] = None
    video_url: Optional[str] = None


# Properties shared by models stored in DB
class LessonInDBBase(LessonBase):
    id: str

    class Config:
        orm_mode = True


# Properties to return via API
class Lesson(LessonInDBBase):
    pass


# Additional properties stored in DB
class LessonInDB(LessonInDBBase):
    pass


# Assignment schemas
class AssignmentBase(BaseModel):
    title: str
    description: str
    due_date: Optional[datetime] = None
    lesson_id: str


class AssignmentCreate(AssignmentBase):
    pass


class AssignmentUpdate(AssignmentBase):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    lesson_id: Optional[str] = None


class AssignmentInDBBase(AssignmentBase):
    id: str

    class Config:
        orm_mode = True


class Assignment(AssignmentInDBBase):
    pass


class AssignmentInDB(AssignmentInDBBase):
    pass


# Submission schemas
class SubmissionBase(BaseModel):
    content: str
    assignment_id: str


class SubmissionCreate(SubmissionBase):
    pass


class SubmissionUpdate(SubmissionBase):
    content: Optional[str] = None
    grade: Optional[float] = None


class SubmissionInDBBase(SubmissionBase):
    id: str
    created_at: datetime
    student_id: str
    grade: Optional[float] = None

    class Config:
        orm_mode = True


class Submission(SubmissionInDBBase):
    pass


class SubmissionInDB(SubmissionInDBBase):
    pass


# Test schemas
class QuestionBase(BaseModel):
    question: str
    options: List[str]
    correct_answer: int


class TestBase(BaseModel):
    title: str
    questions: List[QuestionBase]
    course_id: str


class TestCreate(TestBase):
    pass


class TestUpdate(TestBase):
    title: Optional[str] = None
    questions: Optional[List[QuestionBase]] = None
    course_id: Optional[str] = None


class TestInDBBase(TestBase):
    id: str

    class Config:
        orm_mode = True


class Test(TestInDBBase):
    pass


class TestInDB(TestInDBBase):
    pass


# TestResult schemas
class TestResultBase(BaseModel):
    score: float
    test_id: str


class TestResultCreate(TestResultBase):
    pass


class TestResultInDBBase(TestResultBase):
    id: str
    completed_at: datetime
    user_id: str

    class Config:
        orm_mode = True


class TestResult(TestResultInDBBase):
    pass


class TestResultInDB(TestResultInDBBase):
    pass


# Recommendation schemas
class RecommendationBase(BaseModel):
    score: float
    course_id: str
    user_id: str


class RecommendationCreate(RecommendationBase):
    pass


class RecommendationInDBBase(RecommendationBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True


class Recommendation(RecommendationInDBBase):
    pass


class RecommendationInDB(RecommendationInDBBase):
    pass