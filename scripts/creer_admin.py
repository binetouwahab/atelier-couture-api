from getpass import getpass

from app.db.session import SessionLocal
from app.models.utilisateur import Utilisateur
from app.core.security import hasher_mot_de_passe


def creer_admin():
    db = SessionLocal()

    try:
        print("=== Création du premier administrateur ===")

        email = input("Adresse email : ").strip().lower()
        nom_complet = input("Nom complet : ").strip()
        mot_de_passe = getpass("Mot de passe : ")
        confirmation = getpass("Confirmer le mot de passe : ")

        if not email or not nom_complet:
            print("Erreur : l'email et le nom sont obligatoires.")
            return

        if mot_de_passe != confirmation:
            print("Erreur : les mots de passe ne correspondent pas.")
            return

        if len(mot_de_passe) < 8:
            print("Erreur : le mot de passe doit contenir au moins 8 caractères.")
            return

        utilisateur_existant = db.query(Utilisateur).filter(
            Utilisateur.email == email
        ).first()

        if utilisateur_existant:
            print("Erreur : cet email est déjà utilisé.")
            return

        administrateur = Utilisateur(
            email=email,
            nom_complet=nom_complet,
            mot_de_passe_hash=hasher_mot_de_passe(mot_de_passe),
            role="admin",
            actif=True
        )

        db.add(administrateur)
        db.commit()

        print("Administrateur créé avec succès !")

    except Exception:
        db.rollback()
        print("Une erreur est survenue pendant la création.")

    finally:
        db.close()


if __name__ == "__main__":
    creer_admin()