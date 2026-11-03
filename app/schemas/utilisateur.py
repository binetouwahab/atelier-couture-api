from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UtilisateurCreate(BaseModel):
    email: EmailStr
    nom_complet: str = Field(min_length=2, max_length=150)
    mot_de_passe: str = Field(min_length=8)
    role: Literal["admin", "tailleur", "accueil"]


class UtilisateurUpdate(BaseModel):
    nom_complet: str | None = Field(default=None, min_length=2, max_length=150)
    mot_de_passe: str | None = Field(default=None, min_length=8)
    role: Literal["admin", "tailleur", "accueil"] | None = None
    actif: bool | None = None


class UtilisateurRead(BaseModel):
    id: int
    email: EmailStr
    nom_complet: str
    role: str
    actif: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)