import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.routers.assistant import get_openai_service, get_vector_service as assistant_get_vector_service
from app.routers.matches import get_vector_service as matches_get_vector_service
from app.routers.photos import get_openai_service as photos_get_openai_service
from app.services.openai_service import MockOpenAIService
from app.services.vector_service import MockVectorService
from app.services.auth_service import AuthService


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def mock_openai_service():
    return MockOpenAIService()


@pytest.fixture(scope="function")
def mock_vector_service():
    return MockVectorService()


@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a test user and return (user, token)."""
    auth_service = AuthService(db_session)
    user = auth_service.create_user(
        email="test@example.com",
        username="testuser",
        password="testpassword123"
    )
    token = auth_service.create_access_token(user.id)
    return user, token


@pytest.fixture(scope="function")
def client(db_session, mock_openai_service, mock_vector_service):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_openai_service():
        return mock_openai_service

    def override_get_vector_service():
        return mock_vector_service

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_openai_service] = override_get_openai_service
    app.dependency_overrides[photos_get_openai_service] = override_get_openai_service
    app.dependency_overrides[assistant_get_vector_service] = override_get_vector_service
    app.dependency_overrides[matches_get_vector_service] = override_get_vector_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers(test_user):
    """Return authorization headers with test user token."""
    _, token = test_user
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def test_session(client, test_user, auth_headers):
    """Create a test session for the test user."""
    response = client.post(
        "/api/v1/assistant/session",
        headers=auth_headers
    )
    assert response.status_code == 200
    return response.json()["session_id"]
