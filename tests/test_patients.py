def test_create_patient(client):
    r = client.post(
        "/patients",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@test.com",
            "phone_number": "1234567",
        },
    )

    assert r.status_code == 201
    assert r.json()["email"] == "john@test.com"


def test_get_patient_404(client):
    r = client.get("/patients/999")
    assert r.status_code == 404
