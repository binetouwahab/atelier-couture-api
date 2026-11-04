from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_utilisateur_connecte,
    exiger_roles
)
from app.db.session import get_db

from app.schemas.livraison import (
    LivraisonCreate,
    LivraisonRead,
    LivraisonConfirmer,
    LivraisonListe
)

from app.services.livraison_service import (
    planifier_livraison,
    obtenir_livraison_commande,
    confirmer_livraison,
    lister_livraisons
)


router = APIRouter(
    tags=["Livraisons"],
    dependencies=[Depends(get_utilisateur_connecte)]
)


@router.put(
    "/commandes/{commande_id}/livraison",
    response_model=LivraisonRead
)
def creer_ou_modifier_livraison(
    commande_id: int,
    donnees: LivraisonCreate,
    db: Session = Depends(get_db),
    utilisateur=Depends(exiger_roles("accueil"))
):
    livraison = planifier_livraison(
        db=db,
        commande_id=commande_id,
        donnees=donnees
    )

    db.commit()
    db.refresh(livraison)

    return livraison


@router.get(
    "/commandes/{commande_id}/livraison",
    response_model=LivraisonRead
)
def consulter_livraison_commande(
    commande_id: int,
    db: Session = Depends(get_db)
):
    return obtenir_livraison_commande(
        db=db,
        commande_id=commande_id
    )


@router.post(
    "/commandes/{commande_id}/livraison/confirmer",
    response_model=LivraisonRead
)
def confirmer_livraison_commande(
    commande_id: int,
    donnees: LivraisonConfirmer,
    db: Session = Depends(get_db),
    utilisateur=Depends(exiger_roles("accueil"))
):
    livraison = confirmer_livraison(
        db=db,
        commande_id=commande_id,
        autoriser_solde_impaye=donnees.autoriser_solde_impaye,
        utilisateur_id=utilisateur.id
    )

    db.commit()
    db.refresh(livraison)

    return livraison

from app.services.livraison_service import (
    planifier_livraison,
    obtenir_livraison_commande,
    confirmer_livraison,
    lister_livraisons
)

@router.get(
    "/livraisons",
    response_model=LivraisonListe
)
def consulter_toutes_les_livraisons(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    return lister_livraisons(
        db=db,
        limit=limit,
        offset=offset
    )