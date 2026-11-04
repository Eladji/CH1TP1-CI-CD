"""Cas limites des validations et du stockage."""

import pytest


@pytest.mark.parametrize("field", ["firstName", "lastName", "email", "grade", "field"])
def test_missing_fields_are_rejected(client, valid_student, field):
    valid_student.pop(field)
    response = client.post("/students", json=valid_student)
    assert response.status_code == 400
    assert len(client.get("/students").json()) == 5


@pytest.mark.parametrize("field", ["firstName", "lastName"])
@pytest.mark.parametrize("value", ["  ", " A ", 42, False, [], {}])
def test_invalid_names_are_rejected(client, valid_student, field, value):
    valid_student[field] = value
    assert client.post("/students", json=valid_student).status_code == 400


@pytest.mark.parametrize("grade", [-1, 21, True, "15", [], {}])
def test_invalid_grades_are_rejected(client, valid_student, grade):
    valid_student["grade"] = grade
    assert client.post("/students", json=valid_student).status_code == 400


@pytest.mark.parametrize("grade", [0, 20, 12.5])
def test_grade_boundaries_are_accepted(client, valid_student, grade):
    valid_student["grade"] = grade
    response = client.post("/students", json=valid_student)
    assert response.status_code == 201
    assert response.json()["grade"] == grade


@pytest.mark.parametrize("body", [[], "invalid", 1, True])
def test_non_object_json_is_rejected(client, body):
    assert client.post("/students", json=body).status_code == 400


def test_missing_and_malformed_json_are_rejected(client):
    assert client.post("/students").status_code == 400
    assert (
        client.post(
            "/students", content="{", headers={"Content-Type": "application/json"}
        ).status_code
        == 400
    )


@pytest.mark.parametrize("params", [{"page": 0}, {"limit": 0}, {"order": "wrong"}])
def test_invalid_pagination_is_rejected(client, params):
    assert client.get("/students", params=params).status_code == 400


def test_empty_directory_has_defined_statistics(client):
    for student_id in range(1, 6):
        assert client.delete(f"/students/{student_id}").status_code == 200
    assert client.get("/students/stats").json() == {
        "totalStudents": 0,
        "averageGrade": 0,
        "studentsByField": {"informatique": 0, "mathématiques": 0, "physique": 0, "chimie": 0},
        "bestStudent": None,
    }


def test_names_and_email_are_trimmed_and_id_is_server_generated(client, valid_student):
    valid_student.update(firstName=" Sofia ", email=" sofia@example.com ", id=999)
    response = client.post("/students", json=valid_student)
    assert response.status_code == 201
    assert response.json()["firstName"] == "Sofia"
    assert response.json()["email"] == "sofia@example.com"
    assert response.json()["id"] == 6
