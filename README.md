# Annuaire des étudiants — API REST + CI/CD

API REST de gestion d'un annuaire d'étudiants (TP chapitre 1 — CI/CD & DevOps).
Les données sont stockées **en mémoire** : elles sont réinitialisées à chaque redémarrage.

## Stack

| Rôle | Outil |
| --- | --- |
| Framework web | FastAPI |
| Serveur | Uvicorn |
| Tests | pytest + `fastapi.testclient` (httpx) |
| Couverture | pytest-cov |
| Linter / formateur | Ruff |
| Gestionnaire de paquets | uv |
| CI | GitHub Actions (matrix Python 3.12 / 3.13) |

## Installation

```bash
uv sync --dev
```

## Commandes

| Action | Commande |
| --- | --- |
| Démarrer le serveur | `uv run ch1tp` (http://127.0.0.1:8000) |
| Documentation interactive | http://127.0.0.1:8000/docs |
| Lancer les tests | `uv run pytest` |
| Linter | `uv run ruff check .` |
| Formatage | `uv run ruff format .` |

## Structure

```
tp-chapitre-1/
├── .github/workflows/ci.yml   # Pipeline d'intégration continue
├── src/ch1tp/
│   ├── data.py                # Données en mémoire + reset_data()
│   ├── validation.py          # Règles de validation métier
│   ├── routes.py              # Les 7 endpoints
│   ├── app.py                 # Configuration de l'application (sans serveur)
│   └── __main__.py            # Démarrage du serveur Uvicorn
├── tests/
│   ├── conftest.py            # Fixtures : client HTTP + données remises à zéro
│   ├── test_students_get.py
│   ├── test_students_post.py
│   ├── test_students_put_delete.py
│   └── test_students_stats_search.py
└── pyproject.toml             # Dépendances + config ruff & pytest
```

`app.py` ne démarre aucun serveur : les tests importent l'application directement, sans ouvrir de port.

## Modèle de données

| Propriété | Type | Contraintes |
| --- | --- | --- |
| `id` | entier | auto-généré, unique |
| `firstName` | string | obligatoire, min. 2 caractères |
| `lastName` | string | obligatoire, min. 2 caractères |
| `email` | string | obligatoire, format valide, unique |
| `grade` | nombre | obligatoire, entre 0 et 20 |
| `field` | string | `informatique`, `mathématiques`, `physique` ou `chimie` |

## Endpoints

| Méthode | Route | Description | Codes |
| --- | --- | --- | --- |
| GET | `/students` | Liste des étudiants (tri et pagination optionnels) | 200, 400 |
| GET | `/students/stats` | Statistiques globales | 200 |
| GET | `/students/search?q=` | Recherche par nom ou prénom | 200, 400 |
| GET | `/students/{id}` | Un étudiant | 200, 400, 404 |
| POST | `/students` | Créer un étudiant | 201, 400, 409 |
| PUT | `/students/{id}` | Modifier un étudiant | 200, 400, 404, 409 |
| DELETE | `/students/{id}` | Supprimer un étudiant | 200, 400, 404 |

> Les routes `/students/stats` et `/students/search` sont déclarées **avant** `/students/{id}`,
> sinon `stats` serait interprété comme un identifiant.

### GET /students

```bash
curl http://127.0.0.1:8000/students
```

```json
[
  {
    "id": 1,
    "firstName": "Ahmed",
    "lastName": "Benali",
    "email": "ahmed.benali@edtech.io",
    "grade": 15.5,
    "field": "informatique"
  }
]
```

Bonus — tri et pagination (le total est renvoyé dans l'en-tête `X-Total-Count`) :

```bash
curl "http://127.0.0.1:8000/students?sort=grade&order=desc"
curl "http://127.0.0.1:8000/students?page=2&limit=2"
```

### GET /students/{id}

```bash
curl http://127.0.0.1:8000/students/1    # 200
curl http://127.0.0.1:8000/students/999  # 404
curl http://127.0.0.1:8000/students/abc  # 400
```

### POST /students

```bash
curl -X POST http://127.0.0.1:8000/students \
  -H "Content-Type: application/json" \
  -d '{"firstName":"Sofia","lastName":"Lambert","email":"sofia.lambert@edtech.io","grade":16.5,"field":"mathématiques"}'
```

```json
{
  "id": 6,
  "firstName": "Sofia",
  "lastName": "Lambert",
  "email": "sofia.lambert@edtech.io",
  "grade": 16.5,
  "field": "mathématiques"
}
```

Erreurs : `400` (champ manquant, nom trop court, email invalide, note hors de 0-20, filière inconnue),
`409` (email déjà utilisé). Le corps d'erreur contient la liste des problèmes :

```json
{ "detail": ["Le champ 'email' est obligatoire"] }
```

### PUT /students/{id}

```bash
curl -X PUT http://127.0.0.1:8000/students/1 \
  -H "Content-Type: application/json" \
  -d '{"firstName":"Ahmed","lastName":"Benali","email":"ahmed.benali@edtech.io","grade":17,"field":"informatique"}'
```

### DELETE /students/{id}

```bash
curl -X DELETE http://127.0.0.1:8000/students/1
```

```json
{ "message": "Étudiant 1 supprimé", "student": { "id": 1, "...": "..." } }
```

### GET /students/stats

```json
{
  "totalStudents": 5,
  "averageGrade": 13.6,
  "studentsByField": { "informatique": 2, "mathématiques": 1, "physique": 1, "chimie": 1 },
  "bestStudent": { "id": 2, "firstName": "Lina", "lastName": "Moreau", "grade": 18.0, "...": "..." }
}
```

### GET /students/search

```bash
curl "http://127.0.0.1:8000/students/search?q=ahmed"   # 200, insensible à la casse
curl "http://127.0.0.1:8000/students/search"           # 400, paramètre q manquant
```

## Tests

68 tests ; couverture locale des lignes et branches : 100 % du code applicatif
(hors point de démarrage du serveur). La couverture est affichée à chaque exécution :

```bash
uv run pytest
```

Chaque test repart des données initiales grâce à la fixture `fresh_data`
(qui appelle `reset_data()`), les tests sont donc indépendants et peuvent tourner
dans n'importe quel ordre.

## Pipeline CI

`.github/workflows/ci.yml` se déclenche sur chaque `push` et chaque `pull_request` vers `main` :

```
Checkout → Setup uv + Python (matrix 3.12 / 3.13) → Install → Lint (ruff) → Tests (pytest)
```

Le job tourne en parallèle sur les deux versions de Python ; le rapport de couverture
est publié en artefact. Une seule erreur de lint ou un seul test rouge fait échouer le pipeline.

## Vérification locale et cycle Red → Green

Ce dépôt est autonome, sur la branche `main`, sans remote. Aucun push ni run
GitHub Actions n'a été effectué. Le workflow est fourni pour répondre à la partie
configuration du sujet ; ses deux versions Python sont vérifiées localement.

```bash
./scripts/ci.sh
```

Cette commande installe les dépendances verrouillées, vérifie lint et formatage,
puis lance les tests avec un seuil de couverture de 80 % et produit
`coverage.xml` et `coverage/html/index.html` (non versionnés).
Le point d'entrée du serveur est exclu de la mesure ; les routes, validations,
données et configuration de l'application sont incluses, avec leurs branches.

La démonstration locale et les sorties réelles sont décrites dans
[`docs/demo-red-green.md`](docs/demo-red-green.md). Le rendu local fournit les
journaux rouge et vert à la place des captures GitHub demandées par le sujet.

## Bonus implémentés

- Tri (`?sort=grade&order=desc`) et pagination (`?page=2&limit=2`) avec en-tête `X-Total-Count`
- Couverture de code (pytest-cov) affichée dans le pipeline et publiée en artefact
- 68 tests (> 20), incluant des cas limites (casse, email réutilisé, id non numérique, tri invalide)
- Documentation API complète ci-dessus + Swagger UI sur `/docs`
