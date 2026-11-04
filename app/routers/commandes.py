
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import (
    get_utilisateur_connecte,
    exiger_roles
)

from app.schemas.commande import (
    CommandeCreate,
    CommandeRead
)

from app.services.commande_service import creer_commande


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
