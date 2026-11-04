
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import (
    get_utilisateur_connecte,
    exiger_roles
)

from app.schemas.commande import (
    CommandeCreate,
    CommandeUpdate,
    CommandeRead,
    CommandeListeRead,
    CommandeDetailRead
)

from app.schemas.historique_statut import (
    ChangementStatut,
    HistoriqueStatutRead
)

from app.schemas.ligne_commande import (
    LigneCommandeCreate,
    LigneCommandeRead
)

from app.services.commande_service import (
    creer_commande,
    lister_commandes,
    obtenir_commande,
    modifier_commande,
    changer_statut_commande,
    lister_historique_commande,
    ajouter_ligne_commande,
    supprimer_ligne_commande
)

router = APIRouter(
    tags=["Commandes"],
    dependencies=[Depends(get_utilisateur_connecte)]
)


@router.post(
    "/commandes",
    response_model=CommandeRead,
    status_code=201
)
def creer_une_commande(
    donnees: CommandeCreate,
    db: Session = Depends(get_db),
    utilisateur=Depends(exiger_roles("accueil"))
):
    nouvelle_commande = creer_commande(
        db,
        donnees,
        utilisateur.id
    )

    db.commit()
    db.refresh(nouvelle_commande)

    return nouvelle_commande


@router.get(
    "/commandes",
    response_model=CommandeListeRead
)
def afficher_commandes(
    statut: str | None = None,
    client_id: int | None = Query(default=None, gt=0),
    en_retard: bool | None = None,
    date_min: date | None = None,
    date_max: date | None = None,
    numero: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    return lister_commandes(
        db=db,
        statut=statut,
        client_id=client_id,
        en_retard=en_retard,
        date_min=date_min,
        date_max=date_max,
        numero=numero,
        limit=limit,
        offset=offset
    )


@router.get(
    "/commandes/{commande_id}",
    response_model=CommandeDetailRead
)
def consulter_commande(
    commande_id: int,
    db: Session = Depends(get_db)
):
    return obtenir_commande(
        db=db,
        commande_id=commande_id
    )


@router.patch(
    "/commandes/{commande_id}",
    response_model=CommandeRead
)
def modifier_une_commande(
    commande_id: int,
    donnees: CommandeUpdate,
    db: Session = Depends(get_db),
    utilisateur=Depends(exiger_roles("accueil"))
):
    modifications = donnees.model_dump(
        exclude_unset=True
    )

    commande_modifiee = modifier_commande(
        db=db,
        commande_id=commande_id,
        modifications=modifications
    )

    db.commit()
    db.refresh(commande_modifiee)

    return commande_modifiee


@router.post(
    "/commandes/{commande_id}/statut",
    response_model=CommandeRead
)
def changer_statut(
    commande_id: int,
    donnees: ChangementStatut,
    db: Session = Depends(get_db),
    utilisateur=Depends(get_utilisateur_connecte)
):
    commande_modifiee = changer_statut_commande(
        db=db,
        commande_id=commande_id,
        donnees=donnees,
        utilisateur=utilisateur
    )

    db.commit()
    db.refresh(commande_modifiee)

    return commande_modifiee


@router.get(
    "/commandes/{commande_id}/historique",
    response_model=list[HistoriqueStatutRead]
)
def afficher_historique_commande(
    commande_id: int,
    db: Session = Depends(get_db)
):
    return lister_historique_commande(
        db=db,
        commande_id=commande_id
    )


@router.post(
    "/commandes/{commande_id}/lignes",
    response_model=LigneCommandeRead,
    status_code=201
)
def ajouter_une_ligne(
    commande_id: int,
    donnees: LigneCommandeCreate,
    db: Session = Depends(get_db),
    utilisateur=Depends(exiger_roles("accueil"))
):
    nouvelle_ligne = ajouter_ligne_commande(
        db=db,
        commande_id=commande_id,
        donnees=donnees
    )

    db.commit()
    db.refresh(nouvelle_ligne)

    return nouvelle_ligne

@router.delete(
    "/commandes/{commande_id}/lignes/{ligne_id}",
    status_code=204
)
def supprimer_une_ligne(
    commande_id: int,
    ligne_id: int,
    db: Session = Depends(get_db),
    utilisateur=Depends(exiger_roles("accueil"))
):
    supprimer_ligne_commande(
        db=db,
        commande_id=commande_id,
        ligne_id=ligne_id
    )

    db.commit()

    return