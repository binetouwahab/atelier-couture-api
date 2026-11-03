from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError

from app.core.config import settings

def creer_access_token(donnees: dict) -> str:
    donnees_a_encoder = donnees.copy()

    date_expiration = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    donnees_a_encoder.update({
        "exp": date_expiration
    })

    token = jwt.encode(
        donnees_a_encoder,
        settings.SECRET_KEY,
        algorithm="HS256"
    )

    return token

def verifier_access_token(token: str) -> dict:
    try:
        donnees = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )

        return donnees

    except InvalidTokenError:
        raise ValueError("Jeton invalide ou expiré.")