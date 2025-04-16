# test_lessons.py
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import uuid

from app.core.config import settings
from app.models.course import Course
from app.models.lesson import Lesson


def test_create_lesson(client: TestClient, admin_token: str, db_session: Session):
    # First create a course
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    admin_id = response.json()["id"]

    course_id = str(uuid.uuid4())
    course = Course(
        id=course_id,
        title="Course for Lessons",
        description="This course will have lessons",
        instructor_id=admin_id,
        tags=["lessons", "test"],
        is_published=True
    )
    db_session.add(course)
    db_session.commit()

    # Create a lesson
    lesson_data = {
        "title": "Introduction to Python",
        "content": "This is the content of the introduction to Python lesson.",
        "order": 1,
        "course_id": course_id
    }
    response = client.post(
        f"{settings.API_V1_STR}/lessons/", headers=headers, json=lesson_data
    )

    # Check response
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == "Introduction to Python"
    assert content["content"] == "This is the content of the introduction to Python lesson."
    assert content["order"] == 1
    assert content["course_id"] == course_id
    assert "id" in content


def test_read_lessons_by_course(client: TestClient, admin_token: str, db_session: Session):
    # Create a course
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    admin_id = response.json()["id"]

    course_id = str(uuid.uuid4())
    course = Course(
        id=course_id,
        title="Course with Multiple Lessons",
        description="This course has multiple lessons",
        instructor_id=admin_id,
        tags=["multiple", "lessons", "test"],
        is_published=True
    )
    db_session.add(course)

    # Create multiple lessons
    lessons = [
        Lesson(
            id=str(uuid.uuid4()),
            title=f"Lesson {i}",
            content=f"Content for lesson {i}",
            order=i,
            course_id=course_id
        )
        for i in range(1, 4)  # Create 3 lessons
    ]
    db_session.add_all(lessons)
    db_session.commit()

    # Get lessons by course ID
    response = client.get(
        f"{settings.API_V1_STR}/lessons/course/{course_id}", headers=headers
    )

    # Check response
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, list)
    assert len(content) == 3

    # Check that lessons are in order
    for i, lesson in enumerate(content):
        assert lesson["order"] == i + 1
        assert lesson["title"] == f"Lesson {i + 1}"
        assert lesson["content"] == f"Content for lesson {i + 1}"
        assert lesson["course_id"] == course_id


def test_read_lesson(client: TestClient, admin_token: str, db_session: Session):
    # Create a course
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    admin_id = response.json()["id"]

    course_id = str(uuid.uuid4())
    course = Course(
        id=course_id,
        title="Course for Reading Lesson",
        description="This course has a lesson to read",
        instructor_id=admin_id,
        tags=["read", "lesson", "test"],
        is_published=True
    )
    db_session.add(course)

    # Create a lesson
    lesson_id = str(uuid.uuid4())
    lesson = Lesson(
        id=lesson_id,
        title="Lesson to Read",
        content="This is the content of the lesson to read.",
        order=1,
        course_id=course_id
    )
    db_session.add(lesson)
    db_session.commit()

    # Get lesson by ID
    response = client.get(f"{settings.API_V1_STR}/lessons/{lesson_id}", headers=headers)

    # Check response
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == lesson_id
    assert content["title"] == "Lesson to Read"
    assert content["content"] == "This is the content of the lesson to read."
    assert content["order"] == 1
    assert content["course_id"] == course_id


def test_update_lesson(client: TestClient, admin_token: str, db_session: Session):
    # Create a course
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    admin_id = response.json()["id"]

    course_id = str(uuid.uuid4())
    course = Course(
        id=course_id,
        title="Course for Updating Lesson",
        description="This course has a lesson to update",
        instructor_id=admin_id,
        tags=["update", "lesson", "test"],
        is_published=True
    )
    db_session.add(course)

    # Create a lesson
    lesson_id = str(uuid.uuid4())
    lesson = Lesson(
        id=lesson_id,
        title="Lesson Before Update",
        content="This is the content before update.",
        order=1,
        course_id=course_id
    )
    db_session.add(lesson)
    db_session.commit()

    # Update lesson
    update_data = {
        "title": "Lesson After Update",
        "content": "This is the updated content.",
        "order": 2
    }
    response = client.put(
        f"{settings.API_V1_STR}/lessons/{lesson_id}", headers=headers, json=update_data
    )

    # Check response
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == lesson_id
    assert content["title"] == "Lesson After Update"
    assert content["content"] == "This is the updated content."
    assert content["order"] == 2
    assert content["course_id"] == course_id


def test_delete_lesson(client: TestClient, admin_token: str, db_session: Session):
    # Create a course
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    admin_id = response.json()["id"]

    course_id = str(uuid.uuid4())
    course = Course(
        id=course_id,
        title="Course for Deleting Lesson",
        description="This course has a lesson to delete",
        instructor_id=admin_id,
        tags=["delete", "lesson", "test"],
        is_published=True
    )
    db_session.add(course)

    # Create a lesson
    lesson_id = str(uuid.uuid4())
    lesson = Lesson(
        id=lesson_id,
        title="Lesson to Delete",
        content="This lesson will be deleted.",
        order=1,
        course_id=course_id
    )
    db_session.add(lesson)
    db_session.commit()

    # Delete lesson
    response = client.delete(f"{settings.API_V1_STR}/lessons/{lesson_id}", headers=headers)

    # Check response
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == lesson_id

    # Verify lesson is deleted
    response = client.get(f"{settings.API_V1_STR}/lessons/{lesson_id}", headers=headers)
    assert response.status_code == 404


def test_reorder_lessons(client: TestClient, admin_token: str, db_session: Session):
    # Create a course
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    admin_id = response.json()["id"]

    course_id = str(uuid.uuid4())
    course = Course(
        id=course_id,
        title="Course for Reordering Lessons",
        description="This course has lessons to reorder",
        instructor_id=admin_id,
        tags=["reorder", "lessons", "test"],
        is_published=True
    )
    db_session.add(course)

    # Create multiple lessons
    lesson_ids = [str(uuid.uuid4()) for _ in range(3)]
    lessons = [
        Lesson(
            id=lesson_ids[i],
            title=f"Lesson {i + 1}",
            content=f"Content for lesson {i + 1}",
            order=i + 1,
            course_id=course_id
        )
        for i in range(3)
    ]
    db_session.add_all(lessons)
    db_session.commit()

    # Reorder lessons: swap first and last
    reorder_data = {
        "lesson_orders": [
            {"id": lesson_ids[0], "order": 3},
            {"id": lesson_ids[1], "order": 2},
            {"id": lesson_ids[2], "order": 1}
        ]
    }
    response = client.post(
        f"{settings.API_V1_STR}/lessons/reorder", headers=headers, json=reorder_data
    )

    # Check response
    assert response.status_code == 200
    content = response.json()
    assert "message" in content
    assert "reordered" in content["message"].lower()

    # Verify reordering by getting lessons by course
    response = client.get(
        f"{settings.API_V1_STR}/lessons/course/{course_id}", headers=headers
    )
    content = response.json()

    # Lessons should be ordered by their new order
    assert content[0]["id"] == lesson_ids[2]
    assert content[0]["order"] == 1

    assert content[1]["id"] == lesson_ids[1]
    assert content[1]["order"] == 2

    assert content[2]["id"] == lesson_ids[0]
    assert content[2]["order"] == 3