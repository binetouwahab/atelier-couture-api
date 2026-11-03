
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import (
    exiger_roles,
    get_utilisateur_connecte
)
from app.db.session import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import (
    UtilisateurCreate,
    UtilisateurRead,
    UtilisateurUpdate
)
from app.services.utilisateur_service import (
    creer_utilisateur,
    lister_utilisateurs,
    obtenir_utilisateur,
    modifier_utilisateur
)


router = APIRouter(
    prefix="/utilisateurs",
    tags=["Utilisateurs"],
    dependencies=[Depends(exiger_roles("admin"))]
)


@router.post("/", response_model=UtilisateurRead, status_code=201)
def creer_un_utilisateur(
    donnees: UtilisateurCreate,
    db: Session = Depends(get_db)
):
    nouvel_utilisateur = creer_utilisateur(db, donnees)

    db.commit()
    db.refresh(nouvel_utilisateur)

    return nouvel_utilisateur


@router.get("/", response_model=list[UtilisateurRead])
def lister_les_utilisateurs(
    db: Session = Depends(get_db)
):
    return lister_utilisateurs(db)


@router.get("/{utilisateur_id}", response_model=UtilisateurRead)
def consulter_un_utilisateur(
    utilisateur_id: int,
    db: Session = Depends(get_db)
):
    return obtenir_utilisateur(db, utilisateur_id)


@router.patch("/{utilisateur_id}", response_model=UtilisateurRead)
def modifier_un_utilisateur(
    utilisateur_id: int,
    donnees: UtilisateurUpdate,
    db: Session = Depends(get_db),
    utilisateur_connecte: Utilisateur = Depends(get_utilisateur_connecte)
):
    utilisateur = modifier_utilisateur(
        db,
        utilisateur_id,
        donnees,
        utilisateur_connecte
    )

    db.commit()
    db.refresh(utilisateur)

    return utilisateur
