"""Temporary smoke test for the Saved Programs API.

Run from the backend repository root with:
    PYTHONPATH=src uv run python saved_programs_smoke_test.py
    
"""

from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.api.deps import get_current_user
from app.core.database import Base, get_db
from app.models.models import DegreeType, Program, University, User


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)


def override_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


def seed_data():
    db = TestingSession()
    db.add_all(
        [
            User(
                user_id=1,
                first_name="Test",
                last_name="User",
                email="test@example.com",
                hashed_password="not-used",
            ),
            University(university_id=20, university_name="Test University"),
            Program(
                program_id=10,
                university_id=20,
                program_name="Computer Science PhD",
                degree_type=DegreeType.phd,
            ),
        ]
    )
    db.commit()
    db.close()


app.dependency_overrides[get_db] = override_db
app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(user_id=1)
seed_data()

client = TestClient(app)


def check(label, response, expected_status):
    assert response.status_code == expected_status, (
        f"{label}: expected {expected_status}, "
        f"got {response.status_code}: {response.text}"
    )
    print(f"[PASS] {label}: {response.status_code} {response.json()}")


check(
    "GET empty list",
    client.get("/api/users/1/saved-programs/"),
    200,
)
check(
    "POST existing program",
    client.post("/api/users/1/saved-programs/", json={"program_id": 10}),
    201,
)
check(
    "POST duplicate",
    client.post("/api/users/1/saved-programs/", json={"program_id": 10}),
    400,
)
check(
    "GET saved program",
    client.get("/api/users/1/saved-programs/"),
    200,
)
check(
    "DELETE saved program",
    client.delete("/api/users/1/saved-programs/10"),
    200,
)
check(
    "DELETE missing saved program",
    client.delete("/api/users/1/saved-programs/10"),
    404,
)
check(
    "Wrong user",
    client.get("/api/users/2/saved-programs/"),
    403,
)
check(
    "Missing program",
    client.post("/api/users/1/saved-programs/", json={"program_id": 999}),
    404,
)

print("Saved Programs smoke test: 8/8 passed")
