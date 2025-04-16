# app/db/base.py

from app.db.base_class import Base

# Import all the models here so Alembic can detect them
from app.models.user import User
from app.models.course import Course
from app.models.lesson import Lesson
from app.models.assignment import Assignment
from app.models.submission import Submission
from app.models.test import Test
from app.models.test_result import TestResult
from app.models.chatbot import ChatMessage  # 👈 ОБЯЗАТЕЛЬНО!
