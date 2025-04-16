from sqlalchemy import Table, Column, ForeignKey, String
from app.db.base_class import Base

user_course_association = Table(
    "user_course_association",
    Base.metadata,
    Column("user_id", String, ForeignKey("user.id")),
    Column("course_id", String, ForeignKey("course.id")),
)
