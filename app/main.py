from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.routers import (
    clients,
    mesures,
    auth,
    utilisateurs,
    type_vetement,
    commandes,
    paiements,
    livraisons,
    statistiques
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

app.include_router(
    clients.router,
    prefix=settings.API_V1_PREFIX
)

app.include_router(
    mesures.router,
    prefix=settings.API_V1_PREFIX
)

app.include_router(
    auth.router,
    prefix=settings.API_V1_PREFIX
)

app.include_router(
    utilisateurs.router,
    prefix=settings.API_V1_PREFIX
)

app.include_router(
    type_vetement.router,
    prefix=settings.API_V1_PREFIX
)

app.include_router(
    commandes.router, 
    prefix=settings.API_V1_PREFIX
)

app.include_router(
    paiements.router,
    prefix=settings.API_V1_PREFIX
)

app.include_router(
    livraisons.router,
    prefix=settings.API_V1_PREFIX
)

app.include_router(
    statistiques.router,
    prefix=settings.API_V1_PREFIX
)

@app.get("/health", tags=["Santé"])
def verifier_sante(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="La base de données est indisponible."
        )