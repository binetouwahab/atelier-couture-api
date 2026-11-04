
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
    CommandeRead,
    CommandeListeRead
)

from app.services.commande_service import creer_commande, lister_commandes


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
