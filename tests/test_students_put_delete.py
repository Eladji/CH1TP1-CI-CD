"""Tests de modification et de suppression."""

from ch1tp.data import INITIAL_STUDENTS


def test_put_with_valid_data_returns_200_and_updated_student(client, valid_student):
    response = client.put("/students/1", json=valid_student)
    body = response.json()

    assert response.status_code == 200
    assert body["id"] == 1
    assert body["lastName"] == valid_student["lastName"]
    assert client.get("/students/1").json()["email"] == valid_student["email"]


def test_put_with_unknown_id_returns_404(client, valid_student):
    response = client.put("/students/999", json=valid_student)

    assert response.status_code == 404


def test_put_with_invalid_data_returns_400(client, valid_student):
    valid_student["grade"] = -3

    response = client.put("/students/1", json=valid_student)

    assert response.status_code == 400


def test_put_with_email_taken_by_another_student_returns_409(client, valid_student):
    valid_student["email"] = INITIAL_STUDENTS[1]["email"]

    response = client.put("/students/1", json=valid_student)

    assert response.status_code == 409


def test_put_can_keep_the_same_email(client):
    student = dict(INITIAL_STUDENTS[0])
    del student["id"]
    student["grade"] = 12.0

    response = client.put("/students/1", json=student)

    assert response.status_code == 200
    assert response.json()["grade"] == 12.0


def test_delete_with_valid_id_returns_200(client):
    response = client.delete("/students/1")

    assert response.status_code == 200
    assert "message" in response.json()
    assert client.get("/students/1").status_code == 404
    assert len(client.get("/students").json()) == len(INITIAL_STUDENTS) - 1


def test_delete_with_unknown_id_returns_404(client):
    response = client.delete("/students/999")

    assert response.status_code == 404


def test_delete_with_non_numeric_id_returns_400(client):
    response = client.delete("/students/abc")

    assert response.status_code == 400
