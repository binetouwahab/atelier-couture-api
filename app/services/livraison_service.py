
from datetime import date

from sqlalchemy import func, select


from app.models.historique_statut import HistoriqueStatut
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


def confirmer_livraison(
    db: Session,
    commande_id: int,
    autoriser_solde_impaye: bool,
    utilisateur_id: int
):
    # 1. Vérifier que la commande existe
    commande = db.get(Commande, commande_id)

    if commande is None:
        raise HTTPException(
            status_code=404,
            detail="Commande introuvable."
        )

    # 2. Vérifier que la commande est terminée
    if commande.statut != "terminee":
        raise HTTPException(
            status_code=409,
            detail="La commande doit être terminée avant de confirmer sa livraison."
        )

    # 3. Calculer le solde restant
    solde = commande.montant_total - commande.montant_paye

    # 4. Vérifier que la commande est entièrement payée
    if solde > 0 and not autoriser_solde_impaye:
        raise HTTPException(
            status_code=409,
            detail=f"Livraison impossible : il reste {solde} FCFA à payer."
        )

    # 5. Rechercher une livraison existante
    livraison = (
        db.query(Livraison)
        .filter(Livraison.commande_id == commande_id)
        .first()
    )

    # 6. Créer automatiquement un retrait atelier si nécessaire
    if livraison is None:
        livraison = Livraison(
            commande_id=commande_id,
            mode="retrait_atelier",
            date_prevue=commande.date_livraison_prevue,
            date_effective=date.today(),
            statut="livree"
        )
        db.add(livraison)

    else:
        livraison.date_effective = date.today()
        livraison.statut = "livree"

    # 7. Mettre à jour la commande
    ancien_statut = commande.statut
    commande.statut = "livree"
    commande.date_livraison_reelle = date.today()

    # 8. Préparer le commentaire de l'historique
    commentaire = "Livraison confirmée."

    if solde > 0:
        commentaire = (
            f"Livraison confirmée avec autorisation de solde impayé. "
            f"Montant restant dû : {solde} FCFA."
        )

    # 9. Enregistrer le changement dans l'historique
    historique = HistoriqueStatut(
        commande_id=commande.id,
        ancien_statut=ancien_statut,
        nouveau_statut="livree",
        commentaire=commentaire,
        utilisateur_id=utilisateur_id
    )

    db.add(historique)

    return livraison



def lister_livraisons(db: Session, limit: int = 20, offset: int = 0):
    total = db.scalar(
        select(func.count()).select_from(Livraison)
    )

    livraisons = db.scalars(
        select(Livraison)
        .order_by(Livraison.id.asc())
        .offset(offset)
        .limit(limit)
    ).all()

    return {
        "items": livraisons,
        "total": total,
        "limit": limit,
        "offset": offset
    }