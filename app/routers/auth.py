from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.config import settings

from app.db.session import get_db
from app.schemas.auth import ConnexionRequest, TokenResponse
from app.services.auth_service import authentifier_utilisateur
from app.core.dependencies import get_utilisateur_connecte
from app.schemas.utilisateur import UtilisateurRead
from app.models.utilisateur import Utilisateur

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


@router.get(
    "/auth/me",
    response_model=UtilisateurRead
)
def obtenir_mon_profil(
    utilisateur: Utilisateur = Depends(get_utilisateur_connecte)
):
    return utilisateur