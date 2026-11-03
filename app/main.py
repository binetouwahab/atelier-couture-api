from fastapi import FastAPI

from app.core.config import settings
from app.routers import clients, mesures


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

app.include_router(
    clients.router,
    prefix=settings.API_V1_PREFIX
)