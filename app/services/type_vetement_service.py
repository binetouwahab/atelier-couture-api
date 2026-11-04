from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.type_vetement import TypeVetement
from app.schemas.type_vetement import TypeVetementCreate


def creer_type_vetement(db: Session, donnees: TypeVetementCreate):
    # Vérifier si une prestation porte déjà ce nom
    prestation_existante = db.query(TypeVetement).filter(
        TypeVetement.nom == donnees.nom
    ).first()

    if prestation_existante:
        raise HTTPException(
            status_code=409,
            detail="Une prestation avec ce nom existe déjà."
        )

    # Créer la nouvelle prestation
    nouvelle_prestation = TypeVetement(**donnees.model_dump())

    db.add(nouvelle_prestation)
    db.flush()

    return nouvelle_prestation


def lister_types_vetement(
    db: Session,
    actifs_seulement: bool = True
):
    requete = db.query(TypeVetement)

    if actifs_seulement:
        requete = requete.filter(TypeVetement.actif == True)

    return requete.order_by(TypeVetement.nom.asc()).all()


def obtenir_type_vetement(db: Session, type_vetement_id: int):
    prestation = db.get(TypeVetement, type_vetement_id)

    if prestation is None:
        raise HTTPException(
            status_code=404,
            detail="Prestation introuvable."
        )

    return prestation


def modifier_type_vetement(
    db: Session,
    type_vetement_id: int,
    modifications: dict
):
    prestation = obtenir_type_vetement(db, type_vetement_id)

    # Vérifier que le nouveau nom n'est pas déjà utilisé
    nouveau_nom = modifications.get("nom")

    if nouveau_nom is not None:
        prestation_existante = db.query(TypeVetement).filter(
            TypeVetement.nom == nouveau_nom,
            TypeVetement.id != type_vetement_id
        ).first()

        if prestation_existante:
            raise HTTPException(
                status_code=409,
                detail="Une prestation avec ce nom existe déjà."
            )

    # Appliquer uniquement les champs transmis
    for champ, valeur in modifications.items():
        setattr(prestation, champ, valeur)

    db.flush()

    return prestation