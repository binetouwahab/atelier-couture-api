
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PaiementCreate(BaseModel):
    montant: int = Field(gt=0)
    mode: Literal[
        "especes",
        "wave",
        "orange_money",
        "virement",
        "cheque"
    ]
    reference: str | None = None
    date_paiement: date = Field(default_factory=date.today)


class PaiementRead(BaseModel):
    id: int
    commande_id: int
    montant: int
    mode: Literal[
        "especes",
        "wave",
        "orange_money",
        "virement",
        "cheque"
    ]
    reference: str | None
    date_paiement: date
    enregistre_par_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
