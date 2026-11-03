from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.schemas.utilisateur import UtilisateurUpdate

from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import UtilisateurCreate
from app.core.security import hasher_mot_de_passe


def creer_utilisateur(db: Session, donnees: UtilisateurCreate):
    # Vérifier si l'adresse email existe déjà
    utilisateur_existant = db.scalar(
        select(Utilisateur).where(
            Utilisateur.email == donnees.email
        )
    )

    if utilisateur_existant:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette adresse email est déjà utilisée."
        )

    # Créer le nouvel utilisateur
    nouvel_utilisateur = Utilisateur(
        email=donnees.email,
        nom_complet=donnees.nom_complet,
        mot_de_passe_hash=hasher_mot_de_passe(donnees.mot_de_passe),
        role=donnees.role,
        actif=True
    )

    db.add(nouvel_utilisateur)
    db.flush()

    return nouvel_utilisateur

def lister_utilisateurs(db: Session):
    utilisateurs = db.scalars(
        select(Utilisateur).order_by(Utilisateur.nom_complet)
    ).all()

    return utilisateurs

def obtenir_utilisateur(db: Session, utilisateur_id: int):
    utilisateur = db.get(Utilisateur, utilisateur_id)

    if utilisateur is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable."
        )

    return utilisateur

def modifier_utilisateur(
    db: Session,
    utilisateur_id: int,
    donnees: UtilisateurUpdate,
    utilisateur_connecte: Utilisateur
):
    utilisateur = obtenir_utilisateur(db, utilisateur_id)

    modifications = donnees.model_dump(exclude_unset=True)

    # Vérifier la règle RG24
    if utilisateur.id == utilisateur_connecte.id:

        if modifications.get("actif") is False:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Vous ne pouvez pas désactiver votre propre compte."
            )

        if modifications.get("role") not in (None, "admin"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Vous ne pouvez pas retirer votre propre rôle administrateur."
            )

    # Appliquer les modifications
    for champ, valeur in modifications.items():

        if valeur is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Le champ {champ} ne peut pas être vide."
            )

        if champ == "mot_de_passe":
            utilisateur.mot_de_passe_hash = hasher_mot_de_passe(valeur)

        else:
            setattr(utilisateur, champ, valeur)

    db.flush()

    return utilisateur