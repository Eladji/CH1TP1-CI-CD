"""Point d'entree: demarre le serveur, separe de la definition de l'app."""

import uvicorn


def main() -> None:
    uvicorn.run("ch1tp.app:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
