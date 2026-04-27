import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app

# In-memory SQLite for tests (no PostgreSQL needed)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(client):
    """Create and return admin user (first registered user)."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin@example.com",
            "username": "admin",
            "password": "AdminPass1",
            "full_name": "Admin User",
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def admin_token(client, admin_user):
    """Return a valid admin JWT token."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "AdminPass1"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def regular_user(client, admin_user):
    """Create a regular user (second registration → role = user)."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "username": "regularuser",
            "password": "UserPass1",
            "full_name": "Regular User",
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def user_token(client, regular_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "regularuser", "password": "UserPass1"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def user_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def sample_category(client, admin_headers):
    response = client.post(
        "/api/v1/categories/",
        json={"name": "Electronics", "description": "Electronic products"},
        headers=admin_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def sample_product(client, admin_headers, sample_category):
    response = client.post(
        "/api/v1/products/",
        json={
            "name": "Test Laptop",
            "sku": "LAP-001",
            "price": "999.99",
            "stock_quantity": 50,
            "low_stock_threshold": 5,
            "category_id": sample_category["id"],
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    return response.json()
