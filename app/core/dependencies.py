from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.utilisateur import Utilisateur
from app.core.jwt import verifier_access_token

security = HTTPBearer()

def get_utilisateur_connecte(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    # Récupérer le JWT
    token = credentials.credentials

    # Vérifier le JWT
    try:
        donnees = verifier_access_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Jeton invalide ou expiré.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Récupérer l'identifiant de l'utilisateur
    utilisateur_id = donnees.get("sub")

    if utilisateur_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Jeton invalide.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Rechercher l'utilisateur dans PostgreSQL
    utilisateur = db.get(Utilisateur, int(utilisateur_id))

    if utilisateur is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Vérifier que le compte est actif
    if not utilisateur.actif:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Compte désactivé.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return utilisateur

def exiger_roles(*roles_autorises: str):

    def verifier_role(
        utilisateur: Utilisateur = Depends(get_utilisateur_connecte)
    ):
        if utilisateur.role not in roles_autorises:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous n'avez pas les droits nécessaires."
            )

        return utilisateur

    return verifier_role