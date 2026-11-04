# Démonstration du cycle Red → Green

Le pipeline ne se déclenche que sur un `push` : il faut donc **trois pushes séparés**
(vert, rouge, vert), sinon GitHub Actions ne lance qu'un seul run sur le dernier commit.

## 0. Prérequis : le repository est poussé et le pipeline est vert

```bash
git remote add origin git@github.com:<votre-compte>/<votre-repo>.git
git push -u origin main
```

Onglet **Actions** → le workflow « CI » doit passer au vert sur les deux versions de Python.

## 1. Introduire le bug volontaire (→ pipeline rouge)

On casse le code de statut de la création : `201 Created` devient `200 OK`.
Le test `test_post_with_valid_data_returns_201_and_generated_id` doit échouer.

```bash
sed -i 's/status_code=status.HTTP_201_CREATED/status_code=status.HTTP_200_OK/' src/ch1tp/routes.py
uv run pytest        # doit échouer en local : 1 failed
git commit -am "test: introduire un bug intentionnel pour démontrer le CI"
git push
```

→ Actions : run **rouge** ❌. Capture d'écran → `docs/pipeline-rouge.png`

## 2. Corriger (→ pipeline vert)

```bash
git revert --no-edit HEAD                     # ou le sed inverse
git commit --amend -m "fix: corriger le bug intentionnel"
uv run pytest        # 32 passed
git push
```

→ Actions : run **vert** ✅. Capture d'écran → `docs/pipeline-vert.png`

## Variante : casser le linter plutôt que les tests

Pour montrer que l'étape lint bloque aussi le pipeline, ajouter un `print()`
ou un import inutilisé dans `src/ch1tp/routes.py` : ruff renvoie `T201` / `F401`
et le job s'arrête avant même d'exécuter les tests.
