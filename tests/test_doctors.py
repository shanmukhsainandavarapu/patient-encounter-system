def test_create_doctor(client):
    r = client.post(
        "/doctors",
        json={
            "full_name": "Dr Who",
            "specialization": "General",
        },
    )

    assert r.status_code == 201


def test_get_doctor_404(client):
    r = client.get("/doctors/999")
    assert r.status_code == 404
