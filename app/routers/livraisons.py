
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_utilisateur_connecte, exiger_roles
from app.db.session import get_db
from app.schemas.livraison import LivraisonCreate, LivraisonRead
from app.services.livraison_service import planifier_livraison


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

