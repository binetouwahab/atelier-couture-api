from sqlalchemy import select

from app.core.config import settings
from app.core.security import hasher_mot_de_passe
from app.db.session import SessionLocal
from app.models.utilisateur import Utilisateur
from app.models.type_vetement import TypeVetement


# Catalogue initial prévu dans l'annexe B du projet
CATALOGUE_INITIAL = [
    {
        "nom": "Boubou",
        "description": "Boubou homme en bazin ou brodé",
        "prix_base": 35000,
        "delai_jours": 10,
    },
    {
        "nom": "Costume 2 pièces",
        "description": "Veste et pantalon",
        "prix_base": 85000,
        "delai_jours": 14,
    },
    {
        "nom": "Robe",
        "description": "Robe sur mesure",
        "prix_base": 30000,
        "delai_jours": 7,
    },
    {
        "nom": "Ensemble wax",
        "description": "Tenue deux pièces en wax",
        "prix_base": 25000,
        "delai_jours": 7,
    },
    {
        "nom": "Chemise",
        "description": "Chemise sur mesure",
        "prix_base": 15000,
        "delai_jours": 5,
    },
    {
        "nom": "Pantalon",
        "description": "Pantalon sur mesure",
        "prix_base": 12000,
        "delai_jours": 4,
    },
    {
        "nom": "Retouche",
        "description": "Ourlet, rétrécissement, remplacement de fermeture",
        "prix_base": 3000,
        "delai_jours": 2,
    },
]


def initialiser_donnees():
    # Vérifier les informations du premier administrateur
    email = settings.ADMIN_EMAIL
    nom_complet = settings.ADMIN_NOM_COMPLET
    mot_de_passe = settings.ADMIN_MOT_DE_PASSE

    if not email or not nom_complet or not mot_de_passe:
        raise ValueError(
            "Les variables ADMIN_EMAIL, ADMIN_NOM_COMPLET "
            "et ADMIN_MOT_DE_PASSE doivent être renseignées dans .env."
        )

    email = email.strip().lower()
    nom_complet = nom_complet.strip()

    if not email or not nom_complet:
        raise ValueError("L'email et le nom de l'administrateur sont obligatoires.")

    if len(mot_de_passe) < 8:
        raise ValueError(
            "Le mot de passe administrateur doit contenir au moins 8 caractères."
        )

    db = SessionLocal()

    try:
        # 1. Créer le premier administrateur s'il n'existe pas
        administrateur = db.scalar(
            select(Utilisateur).where(Utilisateur.email == email)
        )

        if administrateur is None:
            administrateur = Utilisateur(
                email=email,
                nom_complet=nom_complet,
                mot_de_passe_hash=hasher_mot_de_passe(mot_de_passe),
                role="admin",
                actif=True,
            )

            db.add(administrateur)
            print("Premier administrateur ajouté.")
        else:
            print("Administrateur déjà existant : aucune modification.")

        # 2. Ajouter les types de vêtements manquants
        for article in CATALOGUE_INITIAL:
            type_existant = db.scalar(
                select(TypeVetement).where(
                    TypeVetement.nom == article["nom"]
                )
            )

            if type_existant is None:
                db.add(TypeVetement(**article, actif=True))
                print(f"Type de vêtement ajouté : {article['nom']}")
            else:
                print(f"Type déjà existant : {article['nom']}")

        # Enregistrer les ajouts dans une seule transaction
        db.commit()

        print("Initialisation terminée avec succès.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def main():
    try:
        initialiser_donnees()
    except Exception as erreur:
        print(f"Erreur pendant l'initialisation : {erreur}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()