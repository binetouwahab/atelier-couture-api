from app.models.commande import Commande
from app.models.mesure import Mesure
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

def obtenir_client(db: Session, client_id: int):
    client = db.get(Client, client_id)

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Client introuvable."
        )

    return client

def lister_clients(db: Session, limit: int = 20, offset: int = 0):
    clients = db.query(Client).offset(offset).limit(limit).all()

    total = db.query(Client).count()

    return {
        "items": clients,
        "total": total,
        "limit": limit,
        "offset": offset
    }

def modifier_client(db: Session, client_id: int, donnees: dict):
    client = obtenir_client(db, client_id)

    # Vérifier l'unicité du téléphone si celui-ci est modifié
    if "telephone" in donnees and donnees["telephone"] != client.telephone:
        client_existant = db.query(Client).filter(
            Client.telephone == donnees["telephone"],
            Client.id != client_id
        ).first()

        if client_existant:
            raise HTTPException(
                status_code=409,
                detail="Ce numéro de téléphone est déjà utilisé."
            )

    # Appliquer les modifications
    for champ, valeur in donnees.items():
        setattr(client, champ, valeur)

    db.flush()

    return client


def supprimer_client(db: Session, client_id: int):
    client = obtenir_client(db, client_id)

    # Vérifier si le client possède des commandes
    commande_existante = db.query(Commande).filter(
        Commande.client_id == client_id
    ).first()

    if commande_existante:
        raise HTTPException(
            status_code=409,
            detail="Impossible de supprimer un client qui possède des commandes."
        )

    # Vérifier si le client possède des mensurations
    mesure_existante = db.query(Mesure).filter(
        Mesure.client_id == client_id
    ).first()

    if mesure_existante:
        raise HTTPException(
            status_code=409,
            detail="Impossible de supprimer un client qui possède des mensurations."
        )

    db.delete(client)
    db.flush()

    return {"message": "Client supprimé avec succès."}