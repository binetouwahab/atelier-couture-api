
from datetime import date
from fastapi import HTTPException

from sqlalchemy import DateTime, cast, func, select
from sqlalchemy.orm import Session

from app.models.commande import Commande
from app.models.paiement import Paiement
from app.models.livraison import Livraison


STATUTS_COMMANDES = [
    "en_attente",
    "en_coupe",
    "en_couture",
    "essayage",
    "retouches",
    "terminee",
    "livree",
    "annulee"
]


def obtenir_tableau_de_bord(db: Session):
    aujourd_hui = date.today()

    debut_mois = aujourd_hui.replace(day=1)

    if aujourd_hui.month == 12:
        debut_mois_suivant = date(
            aujourd_hui.year + 1, 1, 1
        )
    else:
        debut_mois_suivant = date(
            aujourd_hui.year,
            aujourd_hui.month + 1,
            1
        )

    chiffre_affaires_mois = db.scalar(
        select(
            func.coalesce(
                func.sum(Commande.montant_total), 0
            )
        ).where(
            Commande.date_commande >= debut_mois,
            Commande.date_commande < debut_mois_suivant,
            Commande.statut != "annulee"
        )
    )

    encaisse_mois = db.scalar(
        select(
            func.coalesce(
                func.sum(Paiement.montant), 0
            )
        ).where(
            Paiement.date_paiement >= debut_mois,
            Paiement.date_paiement < debut_mois_suivant
        )
    )

    nb_commandes_mois = db.scalar(
        select(
            func.count(Commande.id)
        ).where(
            Commande.date_commande >= debut_mois,
            Commande.date_commande < debut_mois_suivant
        )
    )

    reste_a_encaisser = db.scalar(
        select(
            func.coalesce(
                func.sum(
                    Commande.montant_total - Commande.montant_paye
                ),
                0
            )
        ).where(
            Commande.statut != "annulee"
        )
    )

    commandes_par_statut = {}

    for statut in STATUTS_COMMANDES:
        nombre = db.scalar(
            select(
                func.count(Commande.id)
            ).where(
                Commande.statut == statut
            )
        )

        commandes_par_statut[statut] = nombre

    nb_commandes_en_retard = db.scalar(
        select(
            func.count(Commande.id)
        ).where(
            Commande.date_livraison_prevue < aujourd_hui,
            Commande.statut.notin_(["livree", "annulee"])
        )
    )

    commandes_pretes_a_livrer = db.scalar(
        select(
            func.count(Commande.id)
        ).where(
            Commande.statut == "terminee"
        )
    )

    livraisons_du_jour = db.scalar(
        select(
            func.count(Livraison.id)
        ).where(
            Livraison.date_prevue == aujourd_hui,
            Livraison.statut == "planifiee"
        )
    )

    return {
        "chiffre_affaires_mois": chiffre_affaires_mois,
        "encaisse_mois": encaisse_mois,
        "nb_commandes_mois": nb_commandes_mois,
        "reste_a_encaisser": reste_a_encaisser,
        "commandes_par_statut": commandes_par_statut,
        "nb_commandes_en_retard": nb_commandes_en_retard,
        "commandes_pretes_a_livrer": commandes_pretes_a_livrer,
        "livraisons_du_jour": livraisons_du_jour
    }

def obtenir_chiffre_affaires(
    db: Session,
    granularite: str,
    date_debut: date | None = None,
    date_fin: date | None = None
):
    aujourd_hui = date.today()

    if date_fin is None:
        date_fin = aujourd_hui

    if date_debut is None:
        date_debut = aujourd_hui.replace(day=1)

    if granularite not in ["jour", "mois"]:
        raise HTTPException(
            status_code=422,
            detail="La granularité doit être 'jour' ou 'mois'."
        )

    if date_debut > date_fin:
        raise HTTPException(
            status_code=422,
            detail="La date de début ne peut pas être supérieure à la date de fin."
        )
    unite_sql = "day" if granularite == "jour" else "month"


    periode_commande = func.date_trunc(
        unite_sql,
        cast(Commande.date_commande, DateTime)
    )

    resultats_commandes = db.execute(
        select(
            periode_commande.label("periode"),
            func.sum(Commande.montant_total).label("montant")
        ).where(
            Commande.date_commande >= date_debut,
            Commande.date_commande <= date_fin,
            Commande.statut != "annulee"
        ).group_by(
            periode_commande
        )
    ).all()

    periode_paiement = func.date_trunc(
        unite_sql,
        cast(Paiement.date_paiement, DateTime)
    )

    resultats_paiements = db.execute(
        select(
            periode_paiement.label("periode"),
            func.sum(Paiement.montant).label("montant")
        ).where(
            Paiement.date_paiement >= date_debut,
            Paiement.date_paiement <= date_fin
        ).group_by(
            periode_paiement
        )
    ).all()

    donnees = {}

    for resultat in resultats_commandes:
        periode = resultat.periode.strftime(
            "%Y-%m-%d" if granularite == "jour" else "%Y-%m"
        )

        donnees[periode] = {
            "chiffre_affaires": resultat.montant,
            "encaissements": 0
        }

    for resultat in resultats_paiements:
        periode = resultat.periode.strftime(
            "%Y-%m-%d" if granularite == "jour" else "%Y-%m"
        )

        if periode not in donnees:
            donnees[periode] = {
                "chiffre_affaires": 0,
                "encaissements": 0
            }

        donnees[periode]["encaissements"] = resultat.montant

    return {
        "granularite": granularite,
        "date_debut": date_debut,
        "date_fin": date_fin,
        "items": [
            {
                "periode": periode,
                **donnees[periode]
            }
            for periode in sorted(donnees)
        ]
    }
    