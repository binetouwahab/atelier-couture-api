
import pytest
from fastapi import HTTPException
from app.models.type_vetement import TypeVetement
from datetime import date, timedelta
from app.models.historique_statut import HistoriqueStatut
from app.schemas.historique_statut import ChangementStatut
from app.models.commande import Commande

from app.schemas.commande import CommandeCreate, LigneCommandeCreate
from app.services.commande_service import (
    creer_commande,
    changer_statut_commande,
)
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



def test_refuser_commande_avec_prestation_desactivee(db):
    utilisateur = Utilisateur(
        email="admin_desactive@test.local",
        nom_complet="Administrateur Test",
        mot_de_passe_hash="hash_test",
        role="admin",
        actif=True
    )
    client = Client(
        nom="Fall",
        prenom="Moussa",
        telephone="763333334"
    )
    prestation = TypeVetement(
        nom="Boubou test",
        description="Prestation désactivée",
        prix_base=35000,
        delai_jours=10,
        actif=False
    )

    db.add_all([utilisateur, client, prestation])
    db.commit()

    donnees = CommandeCreate(
        client_id=client.id,
        lignes=[
            LigneCommandeCreate(
                type_vetement_id=prestation.id,
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
    assert erreur.value.detail == "Cette prestation n'est plus disponible."



def test_refuser_remise_superieure_au_montant_des_prestations(db):
    utilisateur = Utilisateur(
        email="admin_remise@test.local",
        nom_complet="Administrateur Test",
        mot_de_passe_hash="hash_test",
        role="admin",
        actif=True
    )

    client = Client(
        nom="Fall",
        prenom="Moussa",
        telephone="763333335"
    )

    prestation = TypeVetement(
        nom="Boubou remise test",
        description="Boubou sur mesure",
        prix_base=35000,
        delai_jours=10,
        actif=True
    )

    db.add_all([utilisateur, client, prestation])
    db.commit()

    donnees = CommandeCreate(
        client_id=client.id,
        remise=40000,
        lignes=[
            LigneCommandeCreate(
                type_vetement_id=prestation.id,
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
        "La remise ne peut pas dépasser le montant des prestations."
    )



def test_refuser_date_livraison_anterieure_a_la_commande(db):
    utilisateur = Utilisateur(
        email="admin_date@test.local",
        nom_complet="Administrateur Test",
        mot_de_passe_hash="hash_test",
        role="admin",
        actif=True
    )

    client = Client(
        nom="Fall",
        prenom="Moussa",
        telephone="763333336"
    )

    prestation = TypeVetement(
        nom="Boubou date test",
        description="Boubou sur mesure",
        prix_base=35000,
        delai_jours=10,
        actif=True
    )

    db.add_all([utilisateur, client, prestation])
    db.commit()

    donnees = CommandeCreate(
        client_id=client.id,
        date_livraison_prevue=date.today() - timedelta(days=1),
        lignes=[
            LigneCommandeCreate(
                type_vetement_id=prestation.id,
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
        "La date de livraison ne peut pas précéder la date de commande."
    )


def test_creer_commande_avec_succes(db):
    utilisateur = Utilisateur(
        email="admin_succes@test.local",
        nom_complet="Administrateur Test",
        mot_de_passe_hash="hash_test",
        role="admin",
        actif=True
    )

    client = Client(
        nom="Fall",
        prenom="Moussa",
        telephone="763333337"
    )

    prestation = TypeVetement(
        nom="Boubou succes test",
        description="Boubou sur mesure",
        prix_base=35000,
        delai_jours=10,
        actif=True
    )

    db.add_all([utilisateur, client, prestation])
    db.commit()

    donnees = CommandeCreate(
        client_id=client.id,
        lignes=[
            LigneCommandeCreate(
                type_vetement_id=prestation.id,
                quantite=1
            )
        ]
    )

    commande = creer_commande(
        db=db,
        donnees=donnees,
        cree_par_id=utilisateur.id
    )

    # Vérifier le numéro de commande
    assert commande.numero == f"CMD-{date.today().year}-00001"

    # Vérifier le statut initial
    assert commande.statut == "en_attente"

    # Vérifier les montants
    assert commande.montant_total == 35000
    assert commande.montant_paye == 0
    assert commande.remise == 0

    # Vérifier la ligne de commande
    assert len(commande.lignes) == 1
    assert commande.lignes[0].prix_unitaire == 35000
    assert commande.lignes[0].quantite == 1

    # Vérifier la date de livraison calculée
    assert commande.date_livraison_prevue == (
        date.today() + timedelta(days=10)
    )

    # Vérifier l'historique initial
    historique = db.query(HistoriqueStatut).filter(
        HistoriqueStatut.commande_id == commande.id
    ).first()

    assert historique is not None
    assert historique.ancien_statut is None
    assert historique.nouveau_statut == "en_attente"
    assert historique.utilisateur_id == utilisateur.id



def test_refuser_transition_statut_non_autorisee(db):
    utilisateur = Utilisateur(
        email="admin_statut@test.local",
        nom_complet="Administrateur Test",
        mot_de_passe_hash="hash_test",
        role="admin",
        actif=True
    )

    client = Client(
        nom="Fall",
        prenom="Moussa",
        telephone="763333338"
    )

    commande = Commande(
        numero=f"CMD-{date.today().year}-00001",
        client_id=1,
        statut="en_attente",
        date_commande=date.today(),
        date_livraison_prevue=date.today() + timedelta(days=10),
        remise=0,
        montant_total=35000,
        montant_paye=0,
        cree_par_id=1
    )

    db.add_all([utilisateur, client])
    db.commit()

    commande.client_id = client.id
    commande.cree_par_id = utilisateur.id

    db.add(commande)
    db.commit()

    donnees = ChangementStatut(
        nouveau_statut="terminee"
    )

    with pytest.raises(HTTPException) as erreur:
        changer_statut_commande(
            db=db,
            commande_id=commande.id,
            donnees=donnees,
            utilisateur=utilisateur
        )

    assert erreur.value.status_code == 409
    assert erreur.value.detail == (
        "Ce changement de statut n'est pas autorisé."
    )
