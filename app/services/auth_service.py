from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.utilisateur import Utilisateur
from app.schemas.auth import ConnexionRequest
from app.core.security import verifier_mot_de_passe
from app.core.jwt import creer_access_token

def authentifier_utilisateur(
    db: Session,
    donnees: ConnexionRequest
):
    # Rechercher l'utilisateur par son email
    utilisateur = db.query(Utilisateur).filter(
        Utilisateur.email == donnees.email
    ).first()

    # Vérifier les identifiants
    if utilisateur is None or not verifier_mot_de_passe(
        donnees.mot_de_passe,
        utilisateur.mot_de_passe_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Vérifier si le compte est actif
    if not utilisateur.actif:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Compte désactivé."
        )

    # Générer le jeton JWT
    token = creer_access_token({
        "sub": str(utilisateur.id),
        "role": utilisateur.role
    })

    return token