from typing import Optional
from datetime import datetime
from pydantic import BaseModel


# Shared properties
class AssignmentBase(BaseModel):
    title: str
    description: str
    due_date: Optional[datetime] = None
    lesson_id: str


# Properties to receive via API on creation
class AssignmentCreate(AssignmentBase):
    pass


# Properties to receive via API on update
class AssignmentUpdate(AssignmentBase):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    lesson_id: Optional[str] = None


# Properties shared by models stored in DB
class AssignmentInDBBase(AssignmentBase):
    id: str

    class Config:
        orm_mode = True


# Properties to return via API
class Assignment(AssignmentInDBBase):
    pass


# Additional properties stored in DB
class AssignmentInDB(AssignmentInDBBase):
    pass