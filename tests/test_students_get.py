"""Tests de lecture: GET /students et GET /students/:id."""

from ch1tp.data import INITIAL_STUDENTS


def test_list_students_returns_200_and_a_list(client):
    response = client.get("/students")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_students_returns_all_initial_students(client):
    response = client.get("/students")
    body = response.json()

    assert len(body) == len(INITIAL_STUDENTS)
    assert [student["id"] for student in body] == [s["id"] for s in INITIAL_STUDENTS]
    assert set(body[0]) == {"id", "firstName", "lastName", "email", "grade", "field"}


def test_get_student_with_valid_id_returns_the_student(client):
    response = client.get("/students/1")

    assert response.status_code == 200
    assert response.json() == INITIAL_STUDENTS[0]


def test_get_student_with_unknown_id_returns_404(client):
    response = client.get("/students/999")

    assert response.status_code == 404
    assert "detail" in response.json()


def test_get_student_with_non_numeric_id_returns_400(client):
    response = client.get("/students/abc")

    assert response.status_code == 400
    assert "detail" in response.json()


def test_list_students_can_be_sorted_by_grade_descending(client):
    response = client.get("/students", params={"sort": "grade", "order": "desc"})
    grades = [student["grade"] for student in response.json()]

    assert response.status_code == 200
    assert grades == sorted(grades, reverse=True)


def test_list_students_can_be_paginated(client):
    response = client.get("/students", params={"page": 2, "limit": 2})
    body = response.json()

    assert response.status_code == 200
    assert len(body) == 2
    assert [student["id"] for student in body] == [3, 4]
    assert response.headers["X-Total-Count"] == str(len(INITIAL_STUDENTS))


def test_list_students_rejects_unknown_sort_field(client):
    response = client.get("/students", params={"sort": "unknown"})

    assert response.status_code == 400
