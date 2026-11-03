from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TypeVetementCreate(BaseModel):
    nom: str = Field(min_length=2, max_length=100)
    description: str | None = None
    prix_base: int = Field(ge=0)
    delai_jours: int = Field(gt=0)
    actif: bool = True

class TypeVetementUpdate(BaseModel):
    nom: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = None
    prix_base: int | None = Field(default=None, ge=0)
    delai_jours: int | None = Field(default=None, gt=0)
    actif: bool | None = None


class TypeVetementRead(BaseModel):
    id: int
    nom: str
    description: str | None
    prix_base: int
    delai_jours: int
    actif: bool

    model_config = ConfigDict(from_attributes=True)