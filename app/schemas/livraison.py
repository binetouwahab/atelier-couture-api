from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class LivraisonCreate(BaseModel):
    mode: Literal["retrait_atelier", "domicile"]
    adresse: str | None = None
    livreur: str | None = None
    date_prevue: date | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def verifier_adresse(self):
        if self.mode == "domicile" and not self.adresse:
            raise ValueError("Une adresse est obligatoire pour une livraison à domicile.")
        return self


class LivraisonUpdate(BaseModel):
    mode: Literal["retrait_atelier", "domicile"] | None = None
    adresse: str | None = None
    livreur: str | None = None
    date_prevue: date | None = None
    notes: str | None = None
@model_validator(mode="after")
def verifier_adresse(self):
    if self.mode == "domicile" and not self.adresse:
        raise ValueError(
            "Une adresse est obligatoire pour une livraison à domicile."
        )
    return self


class LivraisonRead(BaseModel):
    id: int
    commande_id: int
    mode: Literal["retrait_atelier", "domicile"]
    adresse: str | None
    livreur: str | None
    date_prevue: date | None
    date_effective: date | None
    statut: Literal["planifiee", "livree"]
    notes: str | None

    model_config = ConfigDict(from_attributes=True)