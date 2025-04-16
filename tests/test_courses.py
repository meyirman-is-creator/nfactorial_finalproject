# test_courses.py
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import uuid

from app.core.config import settings
from app.models.course import Course
from app.schemas.course import CourseCreate


def test_create_course(client: TestClient, admin_token: str, db_session: Session):
    # Create a course with admin token
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {
        "title": "Test Python Course",
        "description": "Learn Python programming from scratch",
        "instructor_id": None,  # Will be replaced with admin user id
        "tags": ["programming", "python", "beginner"],
        "is_published": True
    }

    # Get admin user id
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    admin_id = response.json()["id"]
    data["instructor_id"] = admin_id

    response = client.post(
        f"{settings.API_V1_STR}/courses/", headers=headers, json=data
    )

    # Check response
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == "Test Python Course"
    assert content["description"] == "Learn Python programming from scratch"
    assert content["instructor_id"] == admin_id
    assert content["tags"] == ["programming", "python", "beginner"]
    assert content["is_published"] is True
    assert "id" in content


def test_read_courses(client: TestClient, admin_token: str, db_session: Session):
    # Create a test course
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    admin_id = response.json()["id"]

    course = Course(
        id=str(uuid.uuid4()),
        title="Another Test Course",
        description="This is another test course",
        instructor_id=admin_id,
        tags=["test", "course"],
        is_published=True
    )
    db_session.add(course)
    db_session.commit()

    # Get all courses
    response = client.get(f"{settings.API_V1_STR}/courses/", headers=headers)

    # Check response
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, list)
    assert len(content) >= 1
    # At least one course should match our test course
    course_found = False
    for course_data in content:
        if course_data["title"] == "Another Test Course":
            course_found = True
            assert course_data["description"] == "This is another test course"
            assert course_data["instructor_id"] == admin_id
    assert course_found


def test_read_course(client: TestClient, admin_token: str, db_session: Session):
    # Create a test course
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    admin_id = response.json()["id"]

    course_id = str(uuid.uuid4())
    course = Course(
        id=course_id,
        title="Course To Read",
        description="This course will be read by ID",
        instructor_id=admin_id,
        tags=["read", "test"],
        is_published=True
    )
    db_session.add(course)
    db_session.commit()

    # Get course by ID
    response = client.get(f"{settings.API_V1_STR}/courses/{course_id}", headers=headers)

    # Check response
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == course_id
    assert content["title"] == "Course To Read"
    assert content["description"] == "This course will be read by ID"
    assert content["instructor_id"] == admin_id


def test_update_course(client: TestClient, admin_token: str, db_session: Session):
    # Create a test course
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    admin_id = response.json()["id"]

    course_id = str(uuid.uuid4())
    course = Course(
        id=course_id,
        title="Course Before Update",
        description="This course will be updated",
        instructor_id=admin_id,
        tags=["update", "test"],
        is_published=True
    )
    db_session.add(course)
    db_session.commit()

    # Update course
    update_data = {
        "title": "Course After Update",
        "description": "This course has been updated",
        "tags": ["updated", "test", "new"]
    }
    response = client.put(
        f"{settings.API_V1_STR}/courses/{course_id}", headers=headers, json=update_data
    )

    # Check response
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == course_id
    assert content["title"] == "Course After Update"
    assert content["description"] == "This course has been updated"
    assert content["tags"] == ["updated", "test", "new"]
    assert content["instructor_id"] == admin_id


def test_delete_course(client: TestClient, admin_token: str, db_session: Session):
    # Create a test course
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    admin_id = response.json()["id"]

    course_id = str(uuid.uuid4())
    course = Course(
        id=course_id,
        title="Course To Delete",
        description="This course will be deleted",
        instructor_id=admin_id,
        tags=["delete", "test"],
        is_published=True
    )
    db_session.add(course)
    db_session.commit()

    # Delete course
    response = client.delete(f"{settings.API_V1_STR}/courses/{course_id}", headers=headers)

    # Check response
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == course_id

    # Verify course is deleted
    response = client.get(f"{settings.API_V1_STR}/courses/{course_id}", headers=headers)
    assert response.status_code == 404


def test_enroll_in_course(client: TestClient, normal_user_token: str, admin_token: str, db_session: Session):
    # Create a test course as admin
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=admin_headers)
    admin_id = response.json()["id"]

    course_id = str(uuid.uuid4())
    course = Course(
        id=course_id,
        title="Course For Enrollment",
        description="This course is available for enrollment",
        instructor_id=admin_id,
        tags=["enroll", "test"],
        is_published=True
    )
    db_session.add(course)
    db_session.commit()

    # Enroll as normal user
    user_headers = {"Authorization": f"Bearer {normal_user_token}"}
    response = client.post(
        f"{settings.API_V1_STR}/courses/{course_id}/enroll", headers=user_headers
    )

    # Check response
    assert response.status_code == 200
    content = response.json()
    assert "message" in content
    assert "enrolled" in content["message"].lower()

    # Verify enrollment by getting enrolled courses
    response = client.get(f"{settings.API_V1_STR}/courses/enrolled", headers=user_headers)
    assert response.status_code == 200
    courses = response.json()
    assert isinstance(courses, list)
    assert len(courses) >= 1

    # Check that our course is in the enrolled list
    course_found = False
    for course_data in courses:
        if course_data["id"] == course_id:
            course_found = True
            assert course_data["title"] == "Course For Enrollment"
    assert course_found