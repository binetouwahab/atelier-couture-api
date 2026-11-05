
import pytest
from fastapi import HTTPException
from app.models.type_vetement import TypeVetement

from app.schemas.commande import CommandeCreate, LigneCommandeCreate
from app.services.commande_service import creer_commande
from app.models.client import Client
from app.models.mesure import Mesure
from app.models.utilisateur import Utilisateur

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


def test_refuser_mensuration_appartenant_a_un_autre_client(db):
    # Créer un utilisateur
    utilisateur = Utilisateur(
        email="tailleur@test.local",
        nom_complet="Tailleur Test",
        mot_de_passe_hash="hash_test",
        role="tailleur",
        actif=True
    )
    db.add(utilisateur)
    db.flush()

    # Créer deux clients différents
    client_a = Client(
        nom="Ndiaye",
        prenom="Aminata",
        telephone="771111111"
    )

    client_b = Client(
        nom="Diop",
        prenom="Fatou",
        telephone="772222222"
    )

    db.add_all([client_a, client_b])
    db.flush()

    # Créer une mensuration appartenant au client A
    mesure = Mesure(
        client_id=client_a.id,
        prise_par_id=utilisateur.id
    )

    db.add(mesure)
    db.commit()

    # Le client B tente d'utiliser la mensuration du client A
    donnees = CommandeCreate(
        client_id=client_b.id,
        mesure_id=mesure.id,
        lignes=[
            LigneCommandeCreate(
                type_vetement_id=1,
                quantite=1
            )
        ]
    )

    with pytest.raises(HTTPException) as erreur:
        creer_commande(
            db=db,
            donnees=donnees,
            cree_par_id=utilisateur.id
        )

    assert erreur.value.status_code == 422
    assert erreur.value.detail == (
        "Cette mensuration n'appartient pas à ce client."
    )


def test_refuser_commande_avec_prestation_inexistante(db):
    # Créer un utilisateur
    utilisateur = Utilisateur(
        email="admin_prestation@test.local",
        nom_complet="Administrateur Test",
        mot_de_passe_hash="hash_test",
        role="admin",
        actif=True
    )
    db.add(utilisateur)

    # Créer un client
    client = Client(
        nom="Fall",
        prenom="Moussa",
        telephone="763333333"
    )
    db.add(client)
    db.commit()

    # Préparer une commande avec un type de vêtement inexistant
    donnees = CommandeCreate(
        client_id=client.id,
        lignes=[
            LigneCommandeCreate(
                type_vetement_id=9999,
                quantite=1
            )
        ]
    )

    # Vérifier que la prestation est introuvable
    with pytest.raises(HTTPException) as erreur:
        creer_commande(
            db=db,
            donnees=donnees,
            cree_par_id=utilisateur.id
        )

    assert erreur.value.status_code == 404
    assert erreur.value.detail == "Prestation introuvable."
