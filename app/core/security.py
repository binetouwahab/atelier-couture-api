from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


def hasher_mot_de_passe(mot_de_passe: str) -> str:
    return password_hash.hash(mot_de_passe)


def verifier_mot_de_passe(
    mot_de_passe: str,
    mot_de_passe_hash: str
) -> bool:
    return password_hash.verify(mot_de_passe, mot_de_passe_hash)