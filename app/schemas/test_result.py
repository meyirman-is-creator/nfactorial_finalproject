# app/schemas/test_result.py

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class TestResultBase(BaseModel):
    test_id: str
    user_id: str
    score: float
    completed_at: Optional[datetime] = None


class TestResultCreate(TestResultBase):
    pass


class TestResultUpdate(BaseModel):
    score: Optional[float] = None
    completed_at: Optional[datetime] = None


class TestResultOut(TestResultBase):
    id: str

    class Config:
        orm_mode = True
