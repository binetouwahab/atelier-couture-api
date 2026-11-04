from fastapi import FastAPI

from app.core.config import settings
from app.routers import (
    clients,
    mesures,
    auth,
    utilisateurs,
    type_vetement,
    commandes,
    paiements,
    livraisons
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