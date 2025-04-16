from typing import Optional, List
from pydantic import BaseModel


# Shared properties
class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_published: bool = False
    category: Optional[str] = None
    difficulty_level: Optional[str] = None
    price: Optional[float] = None


# Properties to receive via API on creation
class CourseCreate(CourseBase):
    instructor_id: str  # обязательное поле при создании


# Properties to receive via API on update
class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None
    category: Optional[str] = None
    difficulty_level: Optional[str] = None
    price: Optional[float] = None


# Properties shared by models stored in DB
class CourseInDBBase(CourseBase):
    id: str
    instructor_id: str

    class Config:
        orm_mode = True


# Properties to return via API
class Course(CourseInDBBase):
    pass


# Additional properties stored in DB
class CourseInDB(CourseInDBBase):
    pass


# Properties to return via API with nested information
class CourseWithDetails(Course):
    lesson_count: int
    assignment_count: int
    test_count: int
