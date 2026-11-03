from typing import Literal
from datetime import datetime
import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ClientCreate(BaseModel):
    nom: str = Field(min_length=2, max_length=100)
    prenom: str = Field(min_length=2, max_length=100)
    telephone: str
    email: EmailStr | None = None
    adresse: str | None = Field(default=None, max_length=255)
    genre: Literal["homme", "femme", "enfant"] | None = None
    notes: str | None = None

    @field_validator("telephone")
    @classmethod
    def valider_telephone(cls, valeur: str) -> str:
        telephone = re.sub(r"[\s.\-()]", "", valeur)

        if not re.fullmatch(r"\+?\d{6,20}", telephone):
            raise ValueError(
                "Le téléphone doit contenir entre 6 et 20 chiffres."
            )

        return telephone


class ClientUpdate(BaseModel):
    nom: str | None = Field(default=None, min_length=2, max_length=100)
    prenom: str | None = Field(default=None, min_length=2, max_length=100)
    telephone: str | None = None
    email: EmailStr | None = None
    adresse: str | None = Field(default=None, max_length=255)
    genre: Literal["homme", "femme", "enfant"] | None = None
    notes: str | None = None

    @field_validator("telephone")
    @classmethod
    def valider_telephone(cls, valeur: str | None) -> str | None:
        if valeur is None:
            return None

        telephone = re.sub(r"[\s.\-()]", "", valeur)

        if not re.fullmatch(r"\+?\d{6,20}", telephone):
            raise ValueError(
                "Le téléphone doit contenir entre 6 et 20 chiffres."
            )

        return telephone


class ClientRead(BaseModel):
    id: int
    nom: str
    prenom: str
    telephone: str
    email: EmailStr | None
    adresse: str | None
    genre: Literal["homme", "femme", "enfant"] | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config =ConfigDict(from_attributes=True) 