"""Endpoints de l'annuaire d'etudiants."""

from typing import Annotated, Any, Literal

from fastapi import APIRouter, Body, HTTPException, Query, Response, status

from ch1tp import data
from ch1tp.validation import validate_student

router = APIRouter(prefix="/students", tags=["students"])

SORTABLE = ("id", "firstName", "lastName", "email", "grade", "field")


def _parse_id(raw_id: str) -> int:
    """Convertit l'id de l'URL, 400 si ce n'est pas un entier."""
    try:
        return int(raw_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"L'identifiant '{raw_id}' n'est pas un nombre valide",
        ) from None


def _get_or_404(raw_id: str) -> dict:
    student = data.find_student(_parse_id(raw_id))
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aucun étudiant avec l'identifiant {raw_id}",
        )
    return student


def _validate_or_400(payload: Any) -> dict:
    cleaned, errors = validate_student(payload)
    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return cleaned


# --- Les routes fixes sont declarees AVANT /students/{student_id} ---


@router.get("")
def list_students(
    response: Response,
    sort: Annotated[str | None, Query(description="Champ de tri")] = None,
    order: Annotated[Literal["asc", "desc"], Query()] = "asc",
    page: Annotated[int | None, Query(ge=1)] = None,
    limit: Annotated[int | None, Query(ge=1, le=100)] = None,
) -> list[dict]:
    """Liste des etudiants, avec tri et pagination optionnels (bonus)."""
    students = list(data.all_students())

    if sort is not None:
        if sort not in SORTABLE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tri impossible sur '{sort}'. Champs autorisés : {', '.join(SORTABLE)}",
            )
        students.sort(
            key=lambda s: s[sort].lower() if isinstance(s[sort], str) else s[sort],
            reverse=order == "desc",
        )

    response.headers["X-Total-Count"] = str(len(students))
    if page is not None or limit is not None:
        page = page or 1
        limit = limit or 10
        start = (page - 1) * limit
        students = students[start : start + limit]

    return students


@router.get("/stats")
def student_stats() -> dict:
    """Statistiques globales sur l'annuaire."""
    students = data.all_students()
    grades = [student["grade"] for student in students]
    by_field = dict.fromkeys(data.FIELDS, 0)
    for student in students:
        by_field[student["field"]] = by_field.get(student["field"], 0) + 1

    return {
        "totalStudents": len(students),
        "averageGrade": round(sum(grades) / len(grades), 2) if grades else 0,
        "studentsByField": by_field,
        "bestStudent": max(students, key=lambda s: s["grade"]) if students else None,
    }


@router.get("/search")
def search_students(q: Annotated[str, Query()] = "") -> list[dict]:
    """Recherche par nom ou prenom, insensible a la casse."""
    term = q.strip().lower()
    if not term:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le paramètre 'q' est obligatoire et ne peut pas être vide",
        )
    return [
        student
        for student in data.all_students()
        if term in student["firstName"].lower() or term in student["lastName"].lower()
    ]


@router.get("/{student_id}")
def get_student(student_id: str) -> dict:
    return _get_or_404(student_id)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_student(payload: Annotated[Any, Body()]) -> dict:
    cleaned = _validate_or_400(payload)
    if data.email_taken(cleaned["email"]):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"L'email '{cleaned['email']}' est déjà utilisé",
        )
    return data.create_student(cleaned)


@router.put("/{student_id}")
def update_student(student_id: str, payload: Annotated[Any, Body()]) -> dict:
    student = _get_or_404(student_id)
    cleaned = _validate_or_400(payload)
    if data.email_taken(cleaned["email"], exclude_id=student["id"]):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"L'email '{cleaned['email']}' est déjà utilisé par un autre étudiant",
        )
    return data.replace_student(student, cleaned)


@router.delete("/{student_id}")
def delete_student(student_id: str) -> dict:
    student = _get_or_404(student_id)
    data.remove_student(student)
    return {"message": f"Étudiant {student['id']} supprimé", "student": student}
