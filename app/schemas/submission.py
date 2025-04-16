from typing import Optional
from datetime import datetime
from pydantic import BaseModel


# Shared properties
class SubmissionBase(BaseModel):
    content: str
    assignment_id: str


# Properties to receive via API on creation
class SubmissionCreate(SubmissionBase):
    pass


# Properties to receive via API on update
class SubmissionUpdate(SubmissionBase):
    content: Optional[str] = None
    grade: Optional[float] = None


# Properties shared by models stored in DB
class SubmissionInDBBase(SubmissionBase):
    id: str
    created_at: datetime
    student_id: str
    grade: Optional[float] = None

    class Config:
        orm_mode = True


# Properties to return via API
class Submission(SubmissionInDBBase):
    pass


# Additional properties stored in DB
class SubmissionInDB(SubmissionInDBBase):
    pass