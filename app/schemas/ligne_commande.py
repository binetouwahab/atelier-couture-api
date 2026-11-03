from pydantic import BaseModel, ConfigDict, Field


class LigneCommandeCreate(BaseModel):
    type_vetement_id: int = Field(gt=0)
    description: str | None = None
    quantite: int = Field(gt=0)
    prix_unitaire: int | None = Field(default=None, ge=0)

class LigneCommandeUpdate(BaseModel):
    type_vetement_id: int | None = Field(default=None, gt=0)
    description: str | None = None
    quantite: int | None = Field(default=None, gt=0)
    prix_unitaire: int | None = Field(default=None, ge=0)

class LigneCommandeRead(BaseModel):
    id: int
    commande_id: int
    type_vetement_id: int
    description: str | None
    quantite: int
    prix_unitaire: int

    model_config = ConfigDict(from_attributes=True)

