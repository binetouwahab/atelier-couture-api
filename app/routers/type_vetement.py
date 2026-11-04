from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_utilisateur_connecte, exiger_roles
from app.db.session import get_db

from app.schemas.type_vetement import (
    TypeVetementCreate,
    TypeVetementUpdate,
    TypeVetementRead
)

from app.services.type_vetement_service import (
    creer_type_vetement,
    lister_types_vetement,
    obtenir_type_vetement,
    modifier_type_vetement
)


router = APIRouter(
    prefix="/catalogue",
    tags=["Catalogue"],
    dependencies=[Depends(get_utilisateur_connecte)]
)


# Ajouter une prestation
@router.post("/", response_model=TypeVetementRead, status_code=201)
def ajouter_prestation(
    donnees: TypeVetementCreate,
    db: Session = Depends(get_db),
    utilisateur=Depends(exiger_roles("admin"))
):
    prestation = creer_type_vetement(db, donnees)

    db.commit()
    db.refresh(prestation)

    return prestation


# Lister les prestations
@router.get("/", response_model=list[TypeVetementRead])
def afficher_catalogue(
    actifs_seulement: bool = True,
    db: Session = Depends(get_db)
):
    return lister_types_vetement(db, actifs_seulement)


# Consulter une prestation
@router.get("/{type_vetement_id}", response_model=TypeVetementRead)
def consulter_prestation(
    type_vetement_id: int,
    db: Session = Depends(get_db)
):
    return obtenir_type_vetement(db, type_vetement_id)


# Modifier une prestation
@router.patch("/{type_vetement_id}", response_model=TypeVetementRead)
def modifier_prestation(
    type_vetement_id: int,
    donnees: TypeVetementUpdate,
    db: Session = Depends(get_db),
    utilisateur=Depends(exiger_roles("admin"))
):
    modifications = donnees.model_dump(exclude_unset=True)

    prestation = modifier_type_vetement(
        db,
        type_vetement_id,
        modifications
    )

    db.commit()
    db.refresh(prestation)

    return prestation