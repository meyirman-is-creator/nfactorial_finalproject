from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings


def test_login_success(client: TestClient, db_session: Session):
    from app.schemas.user import UserCreate
    from app.crud.user import user

    # Create user
    user_in = UserCreate(
        email="test@example.com",
        password="testpassword",
        name="Test User",
        role="student",
    )
    user.create(db_session, obj_in=user_in)

    # Login
    login_data = {
        "username": "test@example.com",
        "password": "testpassword",
    }
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    # Check response
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient, db_session: Session):
    from app.schemas.user import UserCreate
    from app.crud.user import user

    # Create user
    user_in = UserCreate(
        email="test2@example.com",
        password="testpassword",
        name="Test User 2",
        role="student",
    )
    user.create(db_session, obj_in=user_in)

    # Login with wrong password
    login_data = {
        "username": "test2@example.com",
        "password": "wrongpassword",
    }
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)

    # Check response
    assert response.status_code == 400
    content = response.json()
    assert "detail" in content


def test_login_inactive_user(client: TestClient, db_session: Session):
    from app.schemas.user import UserCreate
    from app.crud.user import user

    # Create inactive user
    user_in = UserCreate(
        email="inactive@example.com",
        password="testpassword",
        name="Inactive User",
        role="student",
        is_active=False,
    )
    user.create(db_session, obj_in=user_in)

    # Login with inactive user
    login_data = {
        "username": "inactive@example.com",
        "password": "testpassword",
    }
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)

    # Check response
    assert response.status_code == 400
    content = response.json()
    assert "detail" in content
    assert content["detail"] == "Inactive user"