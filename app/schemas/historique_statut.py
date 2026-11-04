from datetime import datetime

from pydantic import BaseModel, ConfigDict
from typing import Literal
class HistoriqueStatutRead(BaseModel):
    id: int
    commande_id: int
    ancien_statut: str | None
    nouveau_statut: str
    commentaire: str | None
    utilisateur_id: int
    date_changement: datetime

    model_config = ConfigDict(from_attributes=True)

class ChangementStatut(BaseModel):
    nouveau_statut: Literal[
        "en_coupe",
        "en_couture",
        "essayage",
        "retouches",
        "terminee",
        "annulee"
    ]
    commentaire: str | None = None