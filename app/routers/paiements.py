
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_utilisateur_connecte, exiger_roles
from app.db.session import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.paiement import PaiementCreate, PaiementRead
from app.services.paiement_service import (
    enregistrer_paiement,
    lister_paiements_commande,
    supprimer_paiement
)


router = APIRouter(
    tags=["Paiements"],
    dependencies=[Depends(get_utilisateur_connecte)]
)


@router.post(
    "/commandes/{commande_id}/paiements",
    response_model=PaiementRead,
    status_code=status.HTTP_201_CREATED
)
def creer_paiement(
    commande_id: int,
    donnees: PaiementCreate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(exiger_roles("accueil"))
):
    paiement = enregistrer_paiement(
        db=db,
        commande_id=commande_id,
        donnees=donnees,
        utilisateur_id=utilisateur.id
    )

    db.commit()
    db.refresh(paiement)

    return paiement



@router.get(
    "/commandes/{commande_id}/paiements",
    response_model=list[PaiementRead]
)
def consulter_paiements(
    commande_id: int,
    db: Session = Depends(get_db)
):
    return lister_paiements_commande(
        db=db,
        commande_id=commande_id
    )



@router.delete(
    "/paiements/{paiement_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def annuler_paiement(
    paiement_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(exiger_roles("admin"))
):
    supprimer_paiement(
        db=db,
        paiement_id=paiement_id
    )

    db.commit()
