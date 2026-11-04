"""Tests de creation: POST /students."""

from ch1tp.data import INITIAL_STUDENTS


def test_post_with_valid_data_returns_201_and_generated_id(client, valid_student):
    response = client.post("/students", json=valid_student)
    body = response.json()

    assert response.status_code == 201
    assert body["id"] == len(INITIAL_STUDENTS) + 1
    assert body["firstName"] == valid_student["firstName"]
    assert client.get(f"/students/{body['id']}").status_code == 200


def test_post_without_required_field_returns_400(client, valid_student):
    del valid_student["email"]

    response = client.post("/students", json=valid_student)

    assert response.status_code == 400
    assert any("email" in error for error in response.json()["detail"])


def test_post_with_grade_out_of_range_returns_400(client, valid_student):
    valid_student["grade"] = 25

    response = client.post("/students", json=valid_student)

    assert response.status_code == 400


def test_post_with_existing_email_returns_409(client, valid_student):
    valid_student["email"] = INITIAL_STUDENTS[0]["email"].upper()

    response = client.post("/students", json=valid_student)

    assert response.status_code == 409


def test_post_with_invalid_email_format_returns_400(client, valid_student):
    valid_student["email"] = "pas-un-email"

    response = client.post("/students", json=valid_student)

    assert response.status_code == 400


def test_post_with_unknown_field_of_study_returns_400(client, valid_student):
    valid_student["field"] = "philosophie"

    response = client.post("/students", json=valid_student)

    assert response.status_code == 400


def test_post_with_too_short_name_returns_400(client, valid_student):
    valid_student["firstName"] = "S"

    response = client.post("/students", json=valid_student)

    assert response.status_code == 400


def test_post_does_not_reuse_the_id_of_a_deleted_student(client, valid_student):
    client.delete("/students/5")

    created = client.post("/students", json=valid_student).json()

    assert created["id"] == len(INITIAL_STUDENTS) + 1
