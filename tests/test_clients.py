from datetime import date, timedelta

from app.models.commande import Commande
from app.models.utilisateur import Utilisateur
from app.services.client_service import supprimer_client

import pytest
from fastapi import HTTPException

from app.models.client import Client
from app.services.client_service import creer_client, modifier_client
from app.schemas.client import ClientCreate

def test_refuser_deux_clients_avec_le_meme_telephone(db):
    # Créer le premier client
    premier_client = ClientCreate(
        nom="Ndiaye",
        prenom="Aminata",
        telephone="771234567"
    )

    creer_client(db, premier_client)
    db.commit()

    # Préparer un deuxième client avec le même téléphone
    deuxieme_client = ClientCreate(
        nom="Diop",
        prenom="Fatou",
        telephone="771234567"
    )

    # Vérifier que le service refuse le doublon
    with pytest.raises(HTTPException) as erreur:
        creer_client(db, deuxieme_client)

    assert erreur.value.status_code == 409
    assert erreur.value.detail == "Ce numéro de téléphone est déjà utilisé."


def test_refuser_modification_avec_telephone_deja_utilise(db):
    # Créer deux clients avec des numéros différents
    premier_client = Client(
        nom="Ndiaye",
        prenom="Aminata",
        telephone="771234567"
    )

    deuxieme_client = Client(
        nom="Diop",
        prenom="Fatou",
        telephone="781234567"
    )

    db.add_all([premier_client, deuxieme_client])
    db.commit()

    # Tenter de donner au deuxième client le numéro du premier
    with pytest.raises(HTTPException) as erreur:
        modifier_client(
            db,
            deuxieme_client.id,
            {"telephone": "771234567"}
        )

    assert erreur.value.status_code == 409
    assert erreur.value.detail == "Ce numéro de téléphone est déjà utilisé."



def test_refuser_suppression_client_avec_commande(db):
    # Créer un utilisateur qui sera à l'origine de la commande
    utilisateur = Utilisateur(
        email="test@atelier.local",
        nom_complet="Utilisateur Test",
        mot_de_passe_hash="mot_de_passe_hash_test",
        role="admin",
        actif=True
    )

    db.add(utilisateur)
    db.flush()

    # Créer un client
    client = Client(
        nom="Ndiaye",
        prenom="Aminata",
        telephone="771234567"
    )

    db.add(client)
    db.flush()

    # Créer une commande associée au client
    commande = Commande(
        numero="CMD-2026-00001",
        client_id=client.id,
        date_livraison_prevue=date.today() + timedelta(days=7),
        cree_par_id=utilisateur.id
    )

    db.add(commande)
    db.commit()

    # Tenter de supprimer le client
    with pytest.raises(HTTPException) as erreur:
        supprimer_client(db, client.id)

    assert erreur.value.status_code == 409
    assert erreur.value.detail == (
        "Impossible de supprimer un client qui possède des commandes."
    )

