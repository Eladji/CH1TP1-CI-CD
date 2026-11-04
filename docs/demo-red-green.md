# Cycle Red → Green local

Le bug volontaire remplace le statut de création `201` par `200`. Le test
`test_post_with_valid_data_returns_201_and_generated_id` détecte la régression.
Le commit suivant rétablit `201` et toute la suite passe de nouveau.

Les commits `test: introduire un statut erroné pour démontrer la régression` et
`fix(api): rétablir le statut de création 201` conservent ces deux états.
Les sorties réelles sont dans `evidence/red.txt` et `evidence/green.txt`.

Pour reproduire sans changer la branche de travail :

```bash
git worktree add /tmp/tp1-red <hash-du-commit-rouge>
cd /tmp/tp1-red
uv sync --dev
uv run pytest --no-cov tests/test_students_post.py::test_post_with_valid_data_returns_201_and_generated_id
```

Le code de sortie attendu est 1. Sur `main`, `./scripts/ci.sh` doit se terminer
avec le code 0.

Le workflow `.github/workflows/ci.yml` est fourni, mais il n'a été ni publié ni
exécuté sur GitHub. Aucune capture de run distant n'est présentée.
