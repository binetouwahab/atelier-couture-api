from datetime import date
from typing import Literal


from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import (
    get_utilisateur_connecte,
    exiger_roles
)

from app.services.statistique_service import (
    obtenir_tableau_de_bord,
    obtenir_chiffre_affaires
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

@router.get(
    "/statistiques/chiffreaffaires"
)
def consulter_chiffre_affaires(
    granularite: Literal["jour", "mois"] = Query(
        default="jour"
    ),
    date_debut: date | None = None,
    date_fin: date | None = None,
    db: Session = Depends(get_db),
    utilisateur=Depends(exiger_roles("admin"))
):
    return obtenir_chiffre_affaires(
        db=db,
        granularite=granularite,
        date_debut=date_debut,
        date_fin=date_fin
    )