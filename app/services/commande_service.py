
from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.mesure import Mesure
from app.models.type_vetement import TypeVetement
from app.models.commande import Commande
from app.models.ligne_commande import LigneCommande
from app.models.historique_statut import HistoriqueStatut

from app.schemas.commande import CommandeCreate


def creer_commande(
    db: Session,
    donnees: CommandeCreate,
    cree_par_id: int
):
    # 1. Vérifier que le client existe
    client = db.get(Client, donnees.client_id)

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Client introuvable."
        )

    # 2. Vérifier les mensurations
    mesure_id = donnees.mesure_id

    if mesure_id is not None:
        mesure = db.get(Mesure, mesure_id)

        if mesure is None:
            raise HTTPException(
                status_code=404,
                detail="Mensuration introuvable."
            )

        if mesure.client_id != donnees.client_id:
            raise HTTPException(
                status_code=422,
                detail="Cette mensuration n'appartient pas à ce client."
            )

    else:
        # Utiliser la dernière mensuration disponible
        derniere_mesure = (
            db.query(Mesure)
            .filter(Mesure.client_id == donnees.client_id)
            .order_by(
                Mesure.date_prise.desc(),
                Mesure.id.desc()
            )
            .first()
        )

        if derniere_mesure is not None:
            mesure_id = derniere_mesure.id

    # 3. Préparer les lignes de commande
    lignes_a_creer = []
    sous_total = 0
    delai_maximum = 0

    for ligne in donnees.lignes:

        prestation = db.get(
            TypeVetement,
            ligne.type_vetement_id
        )

        if prestation is None:
            raise HTTPException(
                status_code=404,
                detail="Prestation introuvable."
            )

        if not prestation.actif:
            raise HTTPException(
                status_code=422,
                detail="Cette prestation n'est plus disponible."
            )

        prix = (
            ligne.prix_unitaire
            if ligne.prix_unitaire is not None
            else prestation.prix_base
        )

        description = ligne.description or prestation.nom

        sous_total += ligne.quantite * prix

        delai_maximum = max(
            delai_maximum,
            prestation.delai_jours
        )

        lignes_a_creer.append(
            LigneCommande(
                type_vetement_id=prestation.id,
                description=description,
                quantite=ligne.quantite,
                prix_unitaire=prix
            )
        )

    # 4. Vérifier la remise
    if donnees.remise > sous_total:
        raise HTTPException(
            status_code=422,
            detail="La remise ne peut pas dépasser le montant des prestations."
        )

    montant_total = sous_total - donnees.remise

    # 5. Déterminer les dates
    date_commande = date.today()

    date_livraison = (
        donnees.date_livraison_prevue
        if donnees.date_livraison_prevue is not None
        else date_commande + timedelta(days=delai_maximum)
    )

    if date_livraison < date_commande:
        raise HTTPException(
            status_code=422,
            detail="La date de livraison ne peut pas précéder la date de commande."
        )

    # 6. Générer le numéro de commande
    annee = date_commande.year
    prefixe = f"CMD-{annee}-"

    derniere_commande = (
        db.query(Commande)
        .filter(Commande.numero.like(f"{prefixe}%"))
        .order_by(Commande.numero.desc())
        .first()
    )

    if derniere_commande is None:
        prochain_numero = 1
    else:
        dernier_numero = int(
            derniere_commande.numero.split("-")[-1]
        )
        prochain_numero = dernier_numero + 1

    numero = f"{prefixe}{prochain_numero:05d}"

    # 7. Créer la commande
    nouvelle_commande = Commande(
        numero=numero,
        client_id=donnees.client_id,
        mesure_id=mesure_id,
        statut="en_attente",
        date_commande=date_commande,
        date_livraison_prevue=date_livraison,
        remise=donnees.remise,
        montant_total=montant_total,
        montant_paye=0,
        notes=donnees.notes,
        cree_par_id=cree_par_id
    )

    db.add(nouvelle_commande)
    db.flush()

    # 8. Associer les lignes à la commande
    for ligne in lignes_a_creer:
        nouvelle_commande.lignes.append(ligne)

    # 9. Enregistrer le statut initial dans l'historique
    historique = HistoriqueStatut(
        commande_id=nouvelle_commande.id,
        ancien_statut=None,
        nouveau_statut="en_attente",
        commentaire=None,
        utilisateur_id=cree_par_id
    )

    db.add(historique)
    db.flush()

    return nouvelle_commande
