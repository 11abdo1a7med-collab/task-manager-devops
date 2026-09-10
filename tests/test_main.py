import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# قاعدة بيانات SQLite في الذاكرة (منفصلة تمامًا عن PostgreSQL!)
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["version"] == "0.2.0"


def test_health(client):
    assert client.get("/health").json() == {"status": "healthy"}


def test_create_task(client):
    response = client.post(
        "/tasks",
        json={"title": "Test task", "description": "via pytest"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert data["completed"] is False
    assert "id" in data


def test_get_tasks(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_complete_task(client):
    response = client.patch("/tasks/1/complete")
    assert response.status_code == 200
    assert response.json()["completed"] is True


def test_delete_task(client):
    assert client.delete("/tasks/1").status_code == 204
    assert client.get("/tasks/1").status_code == 404