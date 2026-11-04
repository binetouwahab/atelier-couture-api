from app.models.commande import Commande
from app.models.mesure import Mesure
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, select, func

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

def lister_clients(
    db: Session,
    limit: int = 20,
    offset: int = 0,
    q: str | None = None,
    genre: str | None = None
):
    requete = db.query(Client)

    # Recherche par nom, prénom ou téléphone
    if q:
        recherche = f"%{q}%"

        requete = requete.filter(
            or_(
                Client.nom.ilike(recherche),
                Client.prenom.ilike(recherche),
                Client.telephone.ilike(recherche)
            )
        )

    # Filtrer par genre
    if genre:
        requete = requete.filter(Client.genre == genre)

    # Compter les clients correspondant aux filtres
    total = requete.count()

    # Trier par nom puis par prénom et appliquer la pagination
    clients = (
        requete
        .order_by(Client.nom, Client.prenom)
        .offset(offset)
        .limit(limit)
        .all()
    )

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

    # Supprimer les mensurations du client
    db.query(Mesure).filter(
        Mesure.client_id == client_id
    ).delete(synchronize_session=False)

    # Supprimer le client
    db.delete(client)
    db.flush()


def lister_commandes_client(
    db: Session,
    client_id: int,
    limit: int = 20,
    offset: int = 0
):
    # Vérifier que le client existe
    obtenir_client(db, client_id)

    # Compter le nombre total de commandes
    total = db.scalar(
        select(func.count())
        .select_from(Commande)
        .where(Commande.client_id == client_id)
    )

    # Récupérer les commandes les plus récentes
    commandes = db.scalars(
        select(Commande)
        .where(Commande.client_id == client_id)
        .order_by(
            Commande.date_commande.desc(),
            Commande.id.desc()
        )
        .offset(offset)
        .limit(limit)
    ).all()

    return {
        "items": commandes,
        "total": total,
        "limit": limit,
        "offset": offset
    }

def obtenir_resume_client(db: Session, client_id: int):
    # Vérifier que le client existe
    obtenir_client(db, client_id)

    # Exclure les commandes annulées
    conditions = (
        Commande.client_id == client_id,
        Commande.statut != "annulee"
    )

    # Compter les commandes non annulées
    nb_commandes = db.scalar(
        select(func.count())
        .select_from(Commande)
        .where(*conditions)
    )

    # Calculer le chiffre d'affaires
    chiffre_affaires = db.scalar(
        select(func.coalesce(func.sum(Commande.montant_total), 0))
        .where(*conditions)
    )

    # Calculer le montant déjà payé
    total_paye = db.scalar(
        select(func.coalesce(func.sum(Commande.montant_paye), 0))
        .where(*conditions)
    )

    # Calculer le solde restant à payer
    solde_du = db.scalar(
        select(
            func.coalesce(
                func.sum(Commande.montant_total - Commande.montant_paye),
                0
            )
        )
        .where(*conditions)
    )

    # Récupérer la dernière commande du client
    derniere_commande = db.scalars(
        select(Commande)
        .where(Commande.client_id == client_id)
        .order_by(
            Commande.date_commande.desc(),
            Commande.id.desc()
        )
        .limit(1)
    ).first()

    # Vérifier si le client possède des mesures
    mesure_existante = db.scalar(
        select(Mesure.id)
        .where(Mesure.client_id == client_id)
        .limit(1)
    )

    return {
        "nb_commandes": nb_commandes,
        "chiffre_affaires": chiffre_affaires,
        "total_paye": total_paye,
        "solde_du": solde_du,
        "derniere_commande": derniere_commande,
        "a_des_mesures": mesure_existante is not None
    }