
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.utilisateur import Utilisateur
from app.db.session import get_db
from app.schemas.mesure import MesureCreate, MesureRead
from app.core.dependencies import get_utilisateur_connecte

from app.services.mesure_service import (
    creer_mesure,
    lister_mesures_client,
    obtenir_derniere_mesure,
    obtenir_mesure
)


router = APIRouter(
    tags=["Mensurations"],
    dependencies=[Depends(get_utilisateur_connecte)]
)


@router.get(
    "/clients/{client_id}/mesures",
    response_model=list[MesureRead]
)
def lister_mesures(
    client_id: int,
    db: Session = Depends(get_db)
):
    return lister_mesures_client(db, client_id)


@router.get(
    "/clients/{client_id}/mesures/derniere",
    response_model=MesureRead
)
def obtenir_derniere_mesure_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    return obtenir_derniere_mesure(db, client_id)


@router.post(
    "/clients/{client_id}/mesures",
    response_model=MesureRead,
    status_code=201
)
def creer_une_mesure(
    client_id: int,
    donnees: MesureCreate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(get_utilisateur_connecte)
):
    # Vérifier que les identifiants correspondent
    if donnees.client_id != client_id:
        raise HTTPException(
            status_code=422,
            detail="L'identifiant du client dans l'URL ne correspond pas à celui des données."
        )

    nouvelle_mesure = creer_mesure(
        db,
        donnees,
        utilisateur.id
    )

    db.commit()
    db.refresh(nouvelle_mesure)

    return nouvelle_mesure

@router.get(
    "/mesures/{mesure_id}",
    response_model=MesureRead
)
def consulter_mesure(
    mesure_id: int,
    db: Session = Depends(get_db)
):
    return obtenir_mesure(db, mesure_id)