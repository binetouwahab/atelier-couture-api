from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.mesure import Mesure
from app.models.client import Client
from app.schemas.mesure import MesureCreate

def creer_mesure(db: Session, donnees: MesureCreate, prise_par_id: int):
    # Vérifier que le client existe
    client = db.get(Client, donnees.client_id)

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Client introuvable."
        )

    # Créer la mensuration
    nouvelle_mesure = Mesure(
        **donnees.model_dump(),
        prise_par_id=prise_par_id
    )

    db.add(nouvelle_mesure)
    db.flush()

    return nouvelle_mesure

def lister_mesures_client(db: Session, client_id: int):
    # Vérifier que le client existe
    client = db.get(Client, client_id)

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Client introuvable."
        )

    # Récupérer toutes les mensurations du client
    mesures = db.query(Mesure).filter(
        Mesure.client_id == client_id
    ).order_by(Mesure.date_prise.desc()).all()

    return mesures

def obtenir_derniere_mesure(db: Session, client_id: int):
    # Vérifier que le client existe
    client = db.get(Client, client_id)

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Client introuvable."
        )

    # Récupérer la mensuration la plus récente
    mesure = db.query(Mesure).filter(
        Mesure.client_id == client_id
    ).order_by(Mesure.date_prise.desc(), Mesure.id.desc()).first()

    if mesure is None:
        raise HTTPException(
            status_code=404,
            detail="Aucune mensuration enregistrée pour ce client."
        )

    return mesure


def obtenir_mesure(db: Session, mesure_id: int):
    # Rechercher la mensuration par son identifiant
    mesure = db.get(Mesure, mesure_id)

    if mesure is None:
        raise HTTPException(
            status_code=404,
            detail="Mensuration introuvable."
        )

    return mesure