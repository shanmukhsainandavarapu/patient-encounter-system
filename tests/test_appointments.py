from datetime import datetime, timedelta, timezone


def create_patient(client):
    r = client.post(
        "/patients",
        json={
            "first_name": "A",
            "last_name": "B",
            "email": "a@test.com",
            "phone_number": "12345",
        },
    )
    return r.json()["id"]


def create_doctor(client):
    r = client.post(
        "/doctors",
        json={
            "full_name": "Dr Test",
            "specialization": "General",
        },
    )
    return r.json()["id"]


def test_past_appointment_rejected(client):
    pid = create_patient(client)
    did = create_doctor(client)

    past = (
        datetime.now(timezone.utc) - timedelta(days=1)
    ).isoformat()

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


def test_overlap_conflict(client):
    pid = create_patient(client)
    did = create_doctor(client)

    start = (
        datetime.now(timezone.utc) + timedelta(days=1)
    )

    client.post(
        "/appointments",
        json={
            "patient_id": pid,
            "doctor_id": did,
            "start_time": start.isoformat(),
            "duration_minutes": 60,
        },
    )

    r = client.post(
        "/appointments",
        json={
            "patient_id": pid,
            "doctor_id": did,
            "start_time": start.isoformat(),
            "duration_minutes": 30,
        },
    )

    assert r.status_code == 409


def test_back_to_back_allowed(client):
    pid = create_patient(client)
    did = create_doctor(client)

    start = datetime.now(timezone.utc) + timedelta(days=1)

    client.post(
        "/appointments",
        json={
            "patient_id": pid,
            "doctor_id": did,
            "start_time": start.isoformat(),
            "duration_minutes": 30,
        },
    )

    r = client.post(
        "/appointments",
        json={
            "patient_id": pid,
            "doctor_id": did,
            "start_time": (start + timedelta(minutes=30)).isoformat(),
            "duration_minutes": 30,
        },
    )

    assert r.status_code == 201
