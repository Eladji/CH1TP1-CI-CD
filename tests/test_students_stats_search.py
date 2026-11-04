"""Tests des routes /students/stats et /students/search."""

from ch1tp.data import INITIAL_STUDENTS


def test_stats_returns_the_expected_payload(client):
    response = client.get("/students/stats")
    body = response.json()
    expected_average = round(sum(s["grade"] for s in INITIAL_STUDENTS) / len(INITIAL_STUDENTS), 2)

    assert response.status_code == 200
    assert body["totalStudents"] == len(INITIAL_STUDENTS)
    assert body["averageGrade"] == expected_average
    assert body["studentsByField"]["informatique"] == 2
    assert body["bestStudent"]["email"] == "lina.moreau@edtech.io"


def test_stats_follows_the_current_data(client):
    client.delete("/students/2")

    body = client.get("/students/stats").json()

    assert body["totalStudents"] == len(INITIAL_STUDENTS) - 1
    assert body["bestStudent"]["id"] != 2


def test_search_returns_matching_students(client):
    response = client.get("/students/search", params={"q": "ahmed"})
    body = response.json()

    assert response.status_code == 200
    assert len(body) == 2
    assert all(student["firstName"] == "Ahmed" for student in body)


def test_search_is_case_insensitive_and_matches_last_name(client):
    response = client.get("/students/search", params={"q": "MOREAU"})

    assert response.status_code == 200
    assert [student["id"] for student in response.json()] == [2]


def test_search_without_query_parameter_returns_400(client):
    assert client.get("/students/search").status_code == 400
    assert client.get("/students/search", params={"q": "   "}).status_code == 400


def test_search_without_match_returns_an_empty_list(client):
    response = client.get("/students/search", params={"q": "zzz"})

    assert response.status_code == 200
    assert response.json() == []


def test_stats_route_is_not_shadowed_by_the_id_route(client):
    assert client.get("/students/stats").status_code == 200
    assert client.get("/students/search", params={"q": "a"}).status_code == 200


def test_health_endpoint_is_available(client):
    assert client.get("/health").json() == {"status": "ok"}
