from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.commande import Commande

from app.models.mesure import Mesure
from app.models.client import Client
from app.schemas.mesure import MesureCreate, MesureUpdate
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


def modifier_mesure(db: Session, mesure_id: int, modifications: dict):
    # Rechercher la mensuration
    mesure = obtenir_mesure(db, mesure_id)

    # Appliquer uniquement les champs transmis
    for champ, valeur in modifications.items():
        setattr(mesure, champ, valeur)

    # Vérifier qu'au moins une mensuration reste renseignée
    champs_mensurations = [
        "taille_cm", "tour_cou", "carrure_dos",
        "longueur_epaule", "tour_poitrine", "tour_taille",
        "tour_bassin", "longueur_manche", "tour_bras",
        "tour_poignet", "longueur_dos", "longueur_haut",
        "longueur_pantalon", "tour_cuisse", "tour_genou",
        "bas_pantalon", "entrejambe", "longueur_robe"
    ]

    if not any(getattr(mesure, champ) is not None for champ in champs_mensurations):
        raise HTTPException(
            status_code=422,
            detail="Au moins une mensuration doit être renseignée."
        )

    db.flush()

    return mesure

def supprimer_mesure(db: Session, mesure_id: int):
    # Rechercher la mensuration
    mesure = obtenir_mesure(db, mesure_id)

    # Vérifier si une commande utilise cette mensuration
    commande_existante = db.query(Commande).filter(
        Commande.mesure_id == mesure_id
    ).first()

    if commande_existante:
        raise HTTPException(
            status_code=409,
            detail="Impossible de supprimer cette mensuration car elle est utilisée par une commande."
        )

    # Supprimer la mensuration
    db.delete(mesure)
    db.flush()

    return