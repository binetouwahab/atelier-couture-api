from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.mesure import MesureCreate, MesureRead

from app.services.mesure_service import (
    creer_mesure,
    lister_mesures_client,
    obtenir_derniere_mesure
)

router = APIRouter(
    tags=["Mensurations"]
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