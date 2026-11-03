from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

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
    donnees: ConnexionRequest,
    db: Session = Depends(get_db)
):
    token = authentifier_utilisateur(db, donnees)

    return {
        "access_token": token,
        "token_type": "bearer"
    }