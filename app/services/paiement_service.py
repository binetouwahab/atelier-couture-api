
from datetime import date

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.commande import Commande
from app.models.paiement import Paiement
from app.schemas.paiement import PaiementCreate


def enregistrer_paiement(
    db: Session,
    commande_id: int,
    donnees: PaiementCreate,
    utilisateur_id: int
):
    # 1. Vérifier que la commande existe
    commande = db.get(Commande, commande_id)

    if commande is None:
        raise HTTPException(
            status_code=404,
            detail="Commande introuvable."
        )

    # 2. Refuser les paiements sur une commande annulée
    if commande.statut == "annulee":
        raise HTTPException(
            status_code=409,
            detail="Impossible d'enregistrer un paiement sur une commande annulée."
        )

    # 3. Refuser une date de paiement dans le futur
    if donnees.date_paiement > date.today():
        raise HTTPException(
            status_code=422,
            detail="La date du paiement ne peut pas être dans le futur."
        )

    # 4. Calculer le solde restant
    solde = commande.montant_total - commande.montant_paye

    # 5. Vérifier que le paiement ne dépasse pas le solde
    if donnees.montant > solde:
        raise HTTPException(
            status_code=409,
            detail=f"Le paiement dépasse le solde restant de {solde} FCFA."
        )

    # 6. Créer le paiement
    paiement = Paiement(
        commande_id=commande_id,
        montant=donnees.montant,
        mode=donnees.mode,
        reference=donnees.reference,
        date_paiement=donnees.date_paiement,
        enregistre_par_id=utilisateur_id
    )

    db.add(paiement)
    db.flush()

    # 7. Recalculer le montant total payé
    montant_paye = (
        db.query(func.coalesce(func.sum(Paiement.montant), 0))
        .filter(Paiement.commande_id == commande_id)
        .scalar()
    )

    commande.montant_paye = montant_paye

    return paiement
