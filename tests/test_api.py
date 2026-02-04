import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone

from main import app
from database import engine
from models.models import Base

client = TestClient(app)


# -------------------------
# DB SETUP (REAL MYSQL)
# -------------------------
@pytest.fixture(scope="module", autouse=True)
def setup_db():
    """
    Create tables once before all tests.
    Uses SAME MySQL DB as the app.
    """
    Base.metadata.create_all(bind=engine)
    yield
    # ❌ Do NOT drop tables (professors usually don't want destructive cleanup)
    # Base.metadata.drop_all(bind=engine)


# -------------------------
# HELPER FUNCTIONS
# -------------------------
def create_patient():
    response = client.post(
        "/patients",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "phone_number": "9999999999",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_doctor():
    response = client.post(
        "/doctors",
        json={
            "full_name": "Dr Test",
            "specialization": "General",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


# -------------------------
# PATIENT TESTS
# -------------------------
def test_create_patient_success():
    pid = create_patient()
    assert isinstance(pid, int)


def test_get_patient_not_found():
    response = client.get("/patients/99999")
    assert response.status_code == 404


# -------------------------
# DOCTOR TESTS
# -------------------------
def test_create_doctor_success():
    did = create_doctor()
    assert isinstance(did, int)


def test_get_doctor_not_found():
    response = client.get("/doctors/99999")
    assert response.status_code == 404


# -------------------------
# APPOINTMENT TESTS
# -------------------------
def test_past_appointment_rejected():
    pid = create_patient()
    did = create_doctor()

    past_time = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()

    response = client.post(
        "/appointments",
        json={
            "patient_id": pid,
            "doctor_id": did,
            "start_time": past_time,
            "duration_minutes": 30,
        },
    )

    # Your service logic raises ValueError → mapped to 409
    assert response.status_code == 409


def test_appointment_overlap_conflict():
    pid = create_patient()
    did = create_doctor()

    start_time = datetime.now(timezone.utc) + timedelta(days=1)

    # First appointment (valid)
    response1 = client.post(
        "/appointments",
        json={
            "patient_id": pid,
            "doctor_id": did,
            "start_time": start_time.isoformat(),
            "duration_minutes": 60,
        },
    )
    assert response1.status_code == 201

    # Overlapping appointment (same start)
    response2 = client.post(
        "/appointments",
        json={
            "patient_id": pid,
            "doctor_id": did,
            "start_time": start_time.isoformat(),
            "duration_minutes": 30,
        },
    )

    assert response2.status_code == 409


def test_back_to_back_appointment_allowed():
    pid = create_patient()
    did = create_doctor()

    start_time = datetime.now(timezone.utc) + timedelta(days=1)

    # First appointment
    response1 = client.post(
        "/appointments",
        json={
            "patient_id": pid,
            "doctor_id": did,
            "start_time": start_time.isoformat(),
            "duration_minutes": 30,
        },
    )
    assert response1.status_code == 201

    # Back-to-back appointment (starts exactly after first ends)
    response2 = client.post(
        "/appointments",
        json={
            "patient_id": pid,
            "doctor_id": did,
            "start_time": (start_time + timedelta(minutes=30)).isoformat(),
            "duration_minutes": 30,
        },
    )

    assert response2.status_code == 201
