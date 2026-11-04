
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import (
    get_utilisateur_connecte,
    exiger_roles
)

from app.services.statistique_service import (
    obtenir_tableau_de_bord
)


router = APIRouter(
    tags=["Statistiques"],
    dependencies=[Depends(get_utilisateur_connecte)]
)


@router.get(
    "/statistiques/tableau-de-bord"
)
def consulter_tableau_de_bord(
    db: Session = Depends(get_db),
    utilisateur=Depends(exiger_roles("admin"))
):
    return obtenir_tableau_de_bord(db=db)
