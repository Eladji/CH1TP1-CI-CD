"""Validation des donnees etudiant, independante du framework web."""

import re

from ch1tp.data import FIELDS

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
REQUIRED_FIELDS = ("firstName", "lastName", "email", "grade", "field")


def validate_student(payload: object) -> tuple[dict | None, list[str]]:
    """Retourne (donnees nettoyees, erreurs). Les erreurs valent un 400."""
    if not isinstance(payload, dict):
        return None, ["Le corps de la requête doit être un objet JSON"]

    errors: list[str] = []

    for name in REQUIRED_FIELDS:
        if payload.get(name) is None or payload.get(name) == "":
            errors.append(f"Le champ '{name}' est obligatoire")

    first_name = payload.get("firstName")
    last_name = payload.get("lastName")
    for name, value in (("firstName", first_name), ("lastName", last_name)):
        if isinstance(value, str) and len(value.strip()) < 2:
            errors.append(f"Le champ '{name}' doit contenir au moins 2 caractères")
        elif value is not None and value != "" and not isinstance(value, str):
            errors.append(f"Le champ '{name}' doit être une chaîne de caractères")

    email = payload.get("email")
    if (
        email is not None
        and email != ""
        and (not isinstance(email, str) or not EMAIL_PATTERN.match(email.strip()))
    ):
        errors.append("Le champ 'email' doit être une adresse email valide")

    grade = payload.get("grade")
    if grade is not None and grade != "":
        if isinstance(grade, bool) or not isinstance(grade, int | float):
            errors.append("Le champ 'grade' doit être un nombre")
        elif not 0 <= grade <= 20:
            errors.append("Le champ 'grade' doit être compris entre 0 et 20")

    field = payload.get("field")
    if field is not None and field != "" and field not in FIELDS:
        errors.append(f"Le champ 'field' doit valoir une de ces valeurs : {', '.join(FIELDS)}")

    if errors:
        return None, errors

    cleaned = {
        "firstName": first_name.strip(),
        "lastName": last_name.strip(),
        "email": email.strip(),
        "grade": float(grade),
        "field": field,
    }
    return cleaned, []
