from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.ligne_commande import (
    LigneCommandeCreate,
    LigneCommandeRead
)

class CommandeCreate(BaseModel):
    client_id: int = Field(gt=0)
    mesure_id: int | None = Field(default=None, gt=0)
    date_livraison_prevue: date | None = None
    remise: int = Field(default=0, ge=0)
    notes: str | None = None
    lignes: list[LigneCommandeCreate] = Field(min_length=1)

class CommandeUpdate(BaseModel):
    mesure_id: int | None = Field(default=None, gt=0)
    date_livraison_prevue: date | None = None
    remise: int | None = Field(default=None, ge=0)
    notes: str | None = None

class CommandeRead(BaseModel):
    id: int
    numero: str
    client_id: int
    mesure_id: int | None
    statut: str
    date_commande: date
    date_livraison_prevue: date | None
    date_livraison_reelle: date | None
    remise: int
    montant_total: int
    montant_paye: int
    notes: str | None
    cree_par_id: int
    created_at: datetime
    updated_at: datetime

    lignes: list[LigneCommandeRead]

    model_config = ConfigDict(from_attributes=True)

class CommandeClientRead(BaseModel):
    id: int
    numero: str
    client_id: int
    statut: str
    date_commande: date
    date_livraison_prevue: date | None
    montant_total: int
    montant_paye: int

    model_config = ConfigDict(from_attributes=True)

    
class CommandeListeItemRead(BaseModel):
    id: int
    numero: str
    client_id: int
    client_nom: str
    statut: str
    date_commande: date
    date_livraison_prevue: date
    montant_total: int
    montant_paye: int
    solde: int
    en_retard: bool


class CommandeListeRead(BaseModel):
    items: list[CommandeListeItemRead]
    total: int
    limit: int
    offset: int
