from fastapi import FastAPI

from app.core.config import settings
from app.routers import clients, mesures, auth, utilisateurs, type_vetement


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