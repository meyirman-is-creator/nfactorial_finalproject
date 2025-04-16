import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.core.config import settings


# ✅ Используем тестовую PostgreSQL-базу из .env
@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(settings.TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_token(client, db_session):
    from app.schemas.user import UserCreate
    from app.crud.user import user

    admin_in = UserCreate(
        email="admin@example.com",
        password="adminpassword",
        name="Admin",
        role="admin",
    )
    user.create(db_session, obj_in=admin_in)

    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={
            "username": "admin@example.com",
            "password": "adminpassword",
        }
    )
    token = response.json()["access_token"]
    return token


@pytest.fixture(scope="function")
def normal_user_token(client, db_session):
    from app.schemas.user import UserCreate
    from app.crud.user import user

    user_in = UserCreate(
        email="user@example.com",
        password="userpassword",
        name="Normal User",
        role="student",
    )
    user.create(db_session, obj_in=user_in)

    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={
            "username": "user@example.com",
            "password": "userpassword",
        }
    )
    token = response.json()["access_token"]
    return token
