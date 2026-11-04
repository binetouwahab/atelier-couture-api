
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.commande import Commande
from app.models.livraison import Livraison
from app.schemas.livraison import LivraisonCreate


def planifier_livraison(
    db: Session,
    commande_id: int,
    donnees: LivraisonCreate
):
    # 1. Vérifier que la commande existe
    commande = db.get(Commande, commande_id)

    if commande is None:
        raise HTTPException(
            status_code=404,
            detail="Commande introuvable."
        )

    # 2. Refuser la modification d'une commande terminée ou annulée
    if commande.statut in ("livree", "annulee"):
        raise HTTPException(
            status_code=409,
            detail="Cette commande ne peut plus être modifiée."
        )

    # 3. Déterminer la date prévue
    date_prevue = donnees.date_prevue or commande.date_livraison_prevue

    # 4. Vérifier que la date n'est pas antérieure à la commande
    if date_prevue < commande.date_commande:
        raise HTTPException(
            status_code=422,
            detail="La date de livraison ne peut pas être antérieure à la date de commande."
        )

    # 5. Chercher une livraison déjà enregistrée
    livraison = (
        db.query(Livraison)
        .filter(Livraison.commande_id == commande_id)
        .first()
    )

    if livraison is None:
        # 6. Créer une nouvelle livraison
        livraison = Livraison(
            commande_id=commande_id,
            mode=donnees.mode,
            adresse=donnees.adresse,
            livreur=donnees.livreur,
            date_prevue=date_prevue,
            notes=donnees.notes
        )
        db.add(livraison)

    else:
        # 7. Modifier la livraison existante
        livraison.mode = donnees.mode
        livraison.adresse = donnees.adresse
        livraison.livreur = donnees.livreur
        livraison.date_prevue = date_prevue
        livraison.notes = donnees.notes

    # 8. Mettre à jour la date prévue de la commande
    commande.date_livraison_prevue = date_prevue

    return livraison


def obtenir_livraison_commande(
    db: Session,
    commande_id: int
):
    # 1. Vérifier que la commande existe
    commande = db.get(Commande, commande_id)

    if commande is None:
        raise HTTPException(
            status_code=404,
            detail="Commande introuvable."
        )

    # 2. Rechercher la livraison de cette commande
    livraison = (
        db.query(Livraison)
        .filter(Livraison.commande_id == commande_id)
        .first()
    )

    # 3. Vérifier qu'une livraison existe
    if livraison is None:
        raise HTTPException(
            status_code=404,
            detail="Aucune livraison n'est enregistrée pour cette commande."
        )

    return livraison