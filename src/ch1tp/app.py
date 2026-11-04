"""Configuration de l'application (sans demarrage de serveur)."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ch1tp.routes import router

app = FastAPI(
    title="Annuaire des étudiants",
    description="API REST de gestion d'un annuaire d'étudiants (données en mémoire).",
    version="1.0.0",
)
app.include_router(router)


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": "Requête JSON ou paramètres invalides"})


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}
