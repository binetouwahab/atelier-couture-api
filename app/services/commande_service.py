
from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.schemas.historique_statut import (
    ChangementStatut,
    HistoriqueStatutRead
)

from app.models.client import Client
from app.models.mesure import Mesure
from app.models.type_vetement import TypeVetement
from app.models.commande import Commande
from app.models.ligne_commande import LigneCommande
from app.models.historique_statut import HistoriqueStatut
from app.models.paiement import Paiement
from app.models.livraison import Livraison
from app.models.utilisateur import Utilisateur

from app.schemas.commande import (
    CommandeCreate,
    CommandeUpdate
)
from app.schemas.ligne_commande import LigneCommandeCreate

from app.schemas.historique_statut import ChangementStatut

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


def lister_commandes(
    db: Session,
    statut: str | None = None,
    client_id: int | None = None,
    en_retard: bool | None = None,
    date_min: date | None = None,
    date_max: date | None = None,
    numero: str | None = None,
    limit: int = 20,
    offset: int = 0
):
    # 1. Préparer les filtres
    filtres = []

    if statut is not None:
        filtres.append(Commande.statut == statut)

    if client_id is not None:
        filtres.append(Commande.client_id == client_id)

    if date_min is not None:
        filtres.append(Commande.date_commande >= date_min)

    if date_max is not None:
        filtres.append(Commande.date_commande <= date_max)

    if numero is not None:
        filtres.append(Commande.numero.ilike(f"%{numero}%"))

    # 2. Déterminer si une commande est en retard
    condition_retard = and_(
        Commande.date_livraison_prevue < date.today(),
        Commande.statut.notin_(["livree", "annulee"])
    )

    if en_retard is True:
        filtres.append(condition_retard)

    elif en_retard is False:
        filtres.append(~condition_retard)

    # 3. Compter le nombre total de commandes
    requete_total = (
        select(func.count(Commande.id))
        .where(*filtres)
    )

    total = db.scalar(requete_total)

    # 4. Récupérer les commandes et leurs clients
    requete = (
        select(Commande, Client)
        .join(Client, Commande.client_id == Client.id)
        .where(*filtres)
        .order_by(
            Commande.date_commande.desc(),
            Commande.id.desc()
        )
        .offset(offset)
        .limit(limit)
    )

    resultats = db.execute(requete).all()

    # 5. Préparer les données à retourner
    items = []

    for commande, client in resultats:

        solde = commande.montant_total - commande.montant_paye

        est_en_retard = (
            commande.date_livraison_prevue < date.today()
            and commande.statut not in ["livree", "annulee"]
        )

        items.append({
            "id": commande.id,
            "numero": commande.numero,
            "client_id": commande.client_id,
            "client_nom": f"{client.prenom} {client.nom}",
            "statut": commande.statut,
            "date_commande": commande.date_commande,
            "date_livraison_prevue": commande.date_livraison_prevue,
            "montant_total": commande.montant_total,
            "montant_paye": commande.montant_paye,
            "solde": solde,
            "en_retard": est_en_retard
        })

    # 6. Retourner les résultats paginés
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset
    }

def obtenir_commande(db: Session, commande_id: int):

    # 1. Rechercher la commande
    commande = db.get(Commande, commande_id)

    if commande is None:
        raise HTTPException(
            status_code=404,
            detail="Commande introuvable."
        )

    # 2. Récupérer les paiements de cette commande
    paiements = (
        db.query(Paiement)
        .filter(Paiement.commande_id == commande_id)
        .order_by(Paiement.date_paiement.desc())
        .all()
    )

    # 3. Récupérer la livraison, si elle existe
    livraison = (
        db.query(Livraison)
        .filter(Livraison.commande_id == commande_id)
        .first()
    )

    # 4. Calculer le solde restant
    solde = commande.montant_total - commande.montant_paye

    # 5. Vérifier si la commande est en retard
    est_en_retard = (
        commande.date_livraison_prevue < date.today()
        and commande.statut not in ["livree", "annulee"]
    )

    # 6. Préparer les informations détaillées
    return {
        "id": commande.id,
        "numero": commande.numero,
        "client_id": commande.client_id,
        "mesure_id": commande.mesure_id,
        "statut": commande.statut,
        "date_commande": commande.date_commande,
        "date_livraison_prevue": commande.date_livraison_prevue,
        "date_livraison_reelle": commande.date_livraison_reelle,
        "remise": commande.remise,
        "montant_total": commande.montant_total,
        "montant_paye": commande.montant_paye,
        "notes": commande.notes,
        "cree_par_id": commande.cree_par_id,
        "created_at": commande.created_at,
        "updated_at": commande.updated_at,
        "lignes": commande.lignes,
        "paiements": paiements,
        "livraison": livraison,
        "solde": solde,
        "en_retard": est_en_retard
    }

    
def modifier_commande(
    db: Session,
    commande_id: int,
    modifications: dict
):
    # 1. Rechercher la commande
    commande = db.get(Commande, commande_id)

    if commande is None:
        raise HTTPException(
            status_code=404,
            detail="Commande introuvable."
        )

    # 2. Vérifier si la commande peut être modifiée
    if commande.statut in ["livree", "annulee"]:
        raise HTTPException(
            status_code=409,
            detail="Cette commande ne peut plus être modifiée."
        )

    # 3. Vérifier la mensuration, si elle est modifiée
    if "mesure_id" in modifications:
        mesure_id = modifications["mesure_id"]

        if mesure_id is not None:
            mesure = db.get(Mesure, mesure_id)

            if mesure is None:
                raise HTTPException(
                    status_code=404,
                    detail="Mensuration introuvable."
                )

            if mesure.client_id != commande.client_id:
                raise HTTPException(
                    status_code=422,
                    detail="Cette mensuration n'appartient pas à ce client."
                )

        commande.mesure_id = mesure_id

    # 4. Vérifier la date de livraison
    if "date_livraison_prevue" in modifications:
        nouvelle_date = modifications["date_livraison_prevue"]

        if nouvelle_date is None:
            raise HTTPException(
                status_code=422,
                detail="La date de livraison est obligatoire."
            )

        if nouvelle_date < commande.date_commande:
            raise HTTPException(
                status_code=422,
                detail="La date de livraison ne peut pas précéder la date de commande."
            )

        commande.date_livraison_prevue = nouvelle_date

    # 5. Recalculer le montant de la commande
    sous_total = sum(
        ligne.quantite * ligne.prix_unitaire
        for ligne in commande.lignes
    )

    nouvelle_remise = modifications.get(
        "remise",
        commande.remise
    )

    if nouvelle_remise is None:
        raise HTTPException(
        status_code=422,
        detail="La remise ne peut pas être vide."
    )

    if nouvelle_remise > sous_total:
        raise HTTPException(
            status_code=422,
            detail="La remise ne peut pas dépasser le montant des prestations."
        )

    nouveau_montant_total = sous_total - nouvelle_remise

    # 6. Vérifier que le nouveau total couvre les paiements déjà effectués
    if nouveau_montant_total < commande.montant_paye:
        raise HTTPException(
            status_code=409,
            detail="Le nouveau montant ne peut pas être inférieur au montant déjà payé."
        )

    commande.remise = nouvelle_remise
    commande.montant_total = nouveau_montant_total

    # 7. Modifier les notes, si elles sont fournies
    if "notes" in modifications:
        commande.notes = modifications["notes"]

    return commande


def changer_statut_commande(
    db: Session,
    commande_id: int,
    donnees: ChangementStatut,
    utilisateur: Utilisateur
):
    # 1. Rechercher la commande
    commande = db.get(Commande, commande_id)

    if commande is None:
        raise HTTPException(
            status_code=404,
            detail="Commande introuvable."
        )

    # 2. Définir les transitions autorisées
    transitions_autorisees = {
        "en_attente": ["en_coupe", "annulee"],
        "en_coupe": ["en_couture", "annulee"],
        "en_couture": ["essayage", "terminee", "annulee"],
        "essayage": ["retouches", "terminee", "annulee"],
        "retouches": ["essayage", "terminee", "annulee"],
        "terminee": [],
        "livree": [],
        "annulee": []
    }

    ancien_statut = commande.statut
    nouveau_statut = donnees.nouveau_statut

    # 3. Vérifier que le changement est autorisé
    statuts_possibles = transitions_autorisees.get(
        ancien_statut,
        []
    )

    if nouveau_statut not in statuts_possibles:
        raise HTTPException(
            status_code=409,
            detail="Ce changement de statut n'est pas autorisé."
        )

    # 4. Empêcher le tailleur d'annuler une commande
    if nouveau_statut == "annulee" and utilisateur.role == "tailleur":
        raise HTTPException(
            status_code=403,
            detail="Un tailleur ne peut pas annuler une commande."
        )

    # 5. Vérifier le commentaire en cas d'acompte
    if nouveau_statut == "annulee" and commande.montant_paye > 0:
        if not donnees.commentaire or not donnees.commentaire.strip():
            raise HTTPException(
                status_code=422,
                detail="Un commentaire expliquant le remboursement ou l'avoir est obligatoire."
            )

    # 6. Modifier le statut
    commande.statut = nouveau_statut

    # 7. Enregistrer le changement dans l'historique
    historique = HistoriqueStatut(
        commande_id=commande.id,
        ancien_statut=ancien_statut,
        nouveau_statut=nouveau_statut,
        commentaire=donnees.commentaire,
        utilisateur_id=utilisateur.id
    )

    db.add(historique)

    return commande

def lister_historique_commande(
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

    # 2. Récupérer l'historique de la commande
    historique = (
        db.query(HistoriqueStatut)
        .filter(HistoriqueStatut.commande_id == commande_id)
        .order_by(
            HistoriqueStatut.date_changement.asc(),
            HistoriqueStatut.id.asc()
        )
        .all()
    )

    # 3. Retourner l'historique
    return historique

def ajouter_ligne_commande(
    db: Session,
    commande_id: int,
    donnees: LigneCommandeCreate
):
    # 1. Vérifier que la commande existe
    commande = db.get(Commande, commande_id)

    if commande is None:
        raise HTTPException(
            status_code=404,
            detail="Commande introuvable."
        )

    # 2. Vérifier que la commande est encore modifiable
    if commande.statut != "en_attente":
        raise HTTPException(
            status_code=409,
            detail="Les lignes ne peuvent être modifiées que lorsque la commande est en attente."
        )

    # 3. Vérifier que la prestation existe
    prestation = db.get(
        TypeVetement,
        donnees.type_vetement_id
    )

    if prestation is None:
        raise HTTPException(
            status_code=404,
            detail="Prestation introuvable."
        )

    # 4. Vérifier que la prestation est active
    if not prestation.actif:
        raise HTTPException(
            status_code=422,
            detail="Cette prestation n'est plus disponible."
        )

    # 5. Déterminer le prix unitaire
    prix = (
        donnees.prix_unitaire
        if donnees.prix_unitaire is not None
        else prestation.prix_base
    )

    # 6. Créer la nouvelle ligne
    nouvelle_ligne = LigneCommande(
        commande_id=commande.id,
        type_vetement_id=prestation.id,
        description=donnees.description or prestation.nom,
        quantite=donnees.quantite,
        prix_unitaire=prix
    )

    db.add(nouvelle_ligne)
    db.flush()

    # 7. Recalculer le sous-total de toutes les lignes
    sous_total = sum(
        ligne.quantite * ligne.prix_unitaire
        for ligne in commande.lignes
    )

    # 8. Calculer le nouveau montant total
    nouveau_montant_total = sous_total - commande.remise

    # 9. Vérifier que le montant couvre les paiements déjà effectués
    if nouveau_montant_total < commande.montant_paye:
        raise HTTPException(
            status_code=409,
            detail="Le nouveau montant ne peut pas être inférieur au montant déjà payé."
        )

    commande.montant_total = nouveau_montant_total

    return nouvelle_ligne