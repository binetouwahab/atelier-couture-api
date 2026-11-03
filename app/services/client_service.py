from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.client import Client
from app.schemas.client import ClientCreate


def creer_client(db: Session, donnees: ClientCreate):
    # Vérifier si le numéro de téléphone existe déjà
    client_existant = db.query(Client).filter(
        Client.telephone == donnees.telephone
    ).first()

    if client_existant:
        raise HTTPException(
            status_code=409,
            detail="Ce numéro de téléphone est déjà utilisé."
        )

    # Créer le nouvel objet Client
    nouveau_client = Client(**donnees.model_dump())

    # Ajouter le client à la session
    db.add(nouveau_client)

    # Envoyer les changements à la base sans valider la transaction
    db.flush()

    return nouveau_client