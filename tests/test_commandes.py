
import pytest
from fastapi import HTTPException

from app.schemas.commande import CommandeCreate, LigneCommandeCreate
from app.services.commande_service import creer_commande


def test_refuser_commande_pour_client_inexistant(db):
    # Préparer une commande avec un client inexistant
    donnees = CommandeCreate(
        client_id=9999,
        lignes=[
            LigneCommandeCreate(
                type_vetement_id=1,
                quantite=1
            )
        ]
    )

    # Vérifier que la création est refusée
    with pytest.raises(HTTPException) as erreur:
        creer_commande(
            db=db,
            donnees=donnees,
            cree_par_id=1
        )

    assert erreur.value.status_code == 404
    assert erreur.value.detail == "Client introuvable."
