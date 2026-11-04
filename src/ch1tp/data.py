"""Stockage en memoire des etudiants (pas de base de donnees)."""

from copy import deepcopy

FIELDS = ("informatique", "mathématiques", "physique", "chimie")

INITIAL_STUDENTS: list[dict] = [
    {
        "id": 1,
        "firstName": "Ahmed",
        "lastName": "Benali",
        "email": "ahmed.benali@edtech.io",
        "grade": 15.5,
        "field": "informatique",
    },
    {
        "id": 2,
        "firstName": "Lina",
        "lastName": "Moreau",
        "email": "lina.moreau@edtech.io",
        "grade": 18.0,
        "field": "mathématiques",
    },
    {
        "id": 3,
        "firstName": "Youssef",
        "lastName": "Haddad",
        "email": "youssef.haddad@edtech.io",
        "grade": 11.25,
        "field": "physique",
    },
    {
        "id": 4,
        "firstName": "Clara",
        "lastName": "Nguyen",
        "email": "clara.nguyen@edtech.io",
        "grade": 9.5,
        "field": "chimie",
    },
    {
        "id": 5,
        "firstName": "Ahmed",
        "lastName": "Tazi",
        "email": "ahmed.tazi@edtech.io",
        "grade": 13.75,
        "field": "informatique",
    },
]

_students: list[dict] = []
_next_id: int = 1


def reset_data() -> None:
    """Remet les donnees dans leur etat initial (utilise par les tests)."""
    global _students, _next_id
    _students = deepcopy(INITIAL_STUDENTS)
    _next_id = max((student["id"] for student in _students), default=0) + 1


def all_students() -> list[dict]:
    return _students


def find_student(student_id: int) -> dict | None:
    return next((s for s in _students if s["id"] == student_id), None)


def email_taken(email: str, exclude_id: int | None = None) -> bool:
    normalized = email.strip().lower()
    return any(s["email"].lower() == normalized and s["id"] != exclude_id for s in _students)


def create_student(payload: dict) -> dict:
    global _next_id
    student = {"id": _next_id, **payload}
    _next_id += 1
    _students.append(student)
    return student


def replace_student(student: dict, payload: dict) -> dict:
    student.update(payload)
    return student


def remove_student(student: dict) -> None:
    _students.remove(student)


reset_data()
