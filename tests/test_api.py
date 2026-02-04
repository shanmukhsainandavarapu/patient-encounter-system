import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone

from main import app
from database import engine
from models.models import Base

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    # DO NOT drop tables (safe for evaluation)


# -------------------------
# HELPERS
# -------------------------
def create_patient():
    r = client.post(
        "/patients",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "phone_number": "9999999999",
        },
    )
    assert r.status_code == 201
    return r.json()["id"]


def create_doctor():
    r = client.post(
        "/doctors",
        json={
            "full_name": "Dr Test",
            "specialization": "General",
        },
    )
    assert r.status_code == 201
    return r.json()["id"]


# -------------------------
# PATIENT TESTS
# -------------------------
def test_create_patient_success():
    pid = create_patient()
    assert isinstance(pid, int)


def test_get_patient_not_found():
    r = client.get("/patients/99999")
    assert r.status_code == 404


# -------------------------
# DOCTOR TESTS
# -------------------------
def test_create_doctor_success():
    did = create_doctor()
    assert isinstance(did, int)


def test_get_doctor_not_found():
    r = client.get("/doctors/99999")
    assert r.status_code == 404


# -------------------------
# APPOINTMENT TESTS
# -------------------------
def test_past_appointment_rejected():
    pid = create_patient()
    did = create_doctor()

    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()

    r = client.post(
        "/appointments",
        json={
            "patient_id": pid,
            "doctor_id": did,
            "start_time": past,
            "duration_minutes": 30,
        },
    )

    assert r.status_code == 409


def test_appointment_overlap_conflict():
    pid = create_patient()
    did = create_doctor()

    start = datetime.now(timezone.utc) + timedelta(days=1)

    r1 = client.post(
        "/appointments",
        json={
            "patient_id": pid,
            "doctor_id": did,
            "start_time": start.isoformat(),
            "duration_minutes": 60,
        },
    )
    assert r1.status_code == 201

    r2 = client.post(
        "/appointments",
        json={
            "patient_id": pid,
            "doctor_id": did,
            "start_time": start.isoformat(),
            "duration_minutes": 30,
        },
    )
    assert r2.status_code == 409


def test_back_to_back_appointment_allowed():
    pid = create_patient()
    did = create_doctor()

    start = datetime.now(timezone.utc) + timedelta(days=1)

    r1 = client.post(
        "/appointments",
        json={
            "patient_id": pid,
            "doctor_id": did,
            "start_time": start.isoformat(),
            "duration_minutes": 30,
        },
    )
    assert r1.status_code == 201

    r2 = client.post(
        "/appointments",
        json={
            "patient_id": pid,
            "doctor_id": did,
            "start_time": (start + timedelta(minutes=30)).isoformat(),
            "duration_minutes": 30,
        },
    )
    assert r2.status_code == 201
