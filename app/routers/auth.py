from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.config import settings

from app.db.session import get_db
from app.schemas.auth import ConnexionRequest, TokenResponse
from app.services.auth_service import authentifier_utilisateur

router = APIRouter(
    tags=["Authentification"]
)


@router.post(
    "/auth/login",
    response_model=TokenResponse
)
def connexion(
    donnees: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # OAuth2 utilise username pour transmettre l'email
    identifiants = ConnexionRequest(
        email=donnees.username,
        mot_de_passe=donnees.password
    )

    token = authentifier_utilisateur(db, identifiants)

    return {
    "access_token": token,
    "token_type": "bearer",
    "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
}