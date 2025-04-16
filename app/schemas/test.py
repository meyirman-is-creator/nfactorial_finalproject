# app/schemas/test.py

from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class Question(BaseModel):
    question_text: str
    options: List[str]
    correct_answer: str


class TestBase(BaseModel):
    title: str
    course_id: str
    description: Optional[str] = None


class TestCreate(TestBase):
    questions: List[Question]


class TestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class TestOut(TestBase):
    id: str
    created_at: datetime
    class Config:
        orm_mode = True


class TestWithQuestions(TestOut):
    questions: List[Question]

class Test(TestBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True
