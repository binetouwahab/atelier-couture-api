from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MesureCreate(BaseModel):
    client_id: int = Field(gt=0)
    date_prise: date = Field(default_factory=date.today)
    notes: str | None = None

    taille_cm: float | None = Field(default=None, gt=0, le=300)
    tour_cou: float | None = Field(default=None, gt=0, le=300)
    carrure_dos: float | None = Field(default=None, gt=0, le=300)
    longueur_epaule: float | None = Field(default=None, gt=0, le=300)
    tour_poitrine: float | None = Field(default=None, gt=0, le=300)
    tour_taille: float | None = Field(default=None, gt=0, le=300)
    tour_bassin: float | None = Field(default=None, gt=0, le=300)
    longueur_manche: float | None = Field(default=None, gt=0, le=300)
    tour_bras: float | None = Field(default=None, gt=0, le=300)
    tour_poignet: float | None = Field(default=None, gt=0, le=300)
    longueur_dos: float | None = Field(default=None, gt=0, le=300)
    longueur_haut: float | None = Field(default=None, gt=0, le=300)
    longueur_pantalon: float | None = Field(default=None, gt=0, le=300)
    tour_cuisse: float | None = Field(default=None, gt=0, le=300)
    tour_genou: float | None = Field(default=None, gt=0, le=300)
    bas_pantalon: float | None = Field(default=None, gt=0, le=300)
    entrejambe: float | None = Field(default=None, gt=0, le=300)
    longueur_robe: float | None = Field(default=None, gt=0, le=300)

    @model_validator(mode="after")
    def verifier_mensurations(self):
        champs = [
            "taille_cm", "tour_cou", "carrure_dos",
            "longueur_epaule", "tour_poitrine", "tour_taille",
            "tour_bassin", "longueur_manche", "tour_bras",
            "tour_poignet", "longueur_dos", "longueur_haut",
            "longueur_pantalon", "tour_cuisse", "tour_genou",
            "bas_pantalon", "entrejambe", "longueur_robe"
        ]

        if not any(getattr(self, champ) is not None for champ in champs):
            raise ValueError("Au moins une mensuration doit être renseignée.")

        return self


class MesureUpdate(BaseModel):
    date_prise: date | None = None
    notes: str | None = None

    taille_cm: float | None = Field(default=None, gt=0, le=300)
    tour_cou: float | None = Field(default=None, gt=0, le=300)
    carrure_dos: float | None = Field(default=None, gt=0, le=300)
    longueur_epaule: float | None = Field(default=None, gt=0, le=300)
    tour_poitrine: float | None = Field(default=None, gt=0, le=300)
    tour_taille: float | None = Field(default=None, gt=0, le=300)
    tour_bassin: float | None = Field(default=None, gt=0, le=300)
    longueur_manche: float | None = Field(default=None, gt=0, le=300)
    tour_bras: float | None = Field(default=None, gt=0, le=300)
    tour_poignet: float | None = Field(default=None, gt=0, le=300)
    longueur_dos: float | None = Field(default=None, gt=0, le=300)
    longueur_haut: float | None = Field(default=None, gt=0, le=300)
    longueur_pantalon: float | None = Field(default=None, gt=0, le=300)
    tour_cuisse: float | None = Field(default=None, gt=0, le=300)
    tour_genou: float | None = Field(default=None, gt=0, le=300)
    bas_pantalon: float | None = Field(default=None, gt=0, le=300)
    entrejambe: float | None = Field(default=None, gt=0, le=300)
    longueur_robe: float | None = Field(default=None, gt=0, le=300)


class MesureRead(BaseModel):
    id: int
    client_id: int
    date_prise: date
    prise_par_id: int
    notes: str | None

    taille_cm: float | None
    tour_cou: float | None
    carrure_dos: float | None
    longueur_epaule: float | None
    tour_poitrine: float | None
    tour_taille: float | None
    tour_bassin: float | None
    longueur_manche: float | None
    tour_bras: float | None
    tour_poignet: float | None
    longueur_dos: float | None
    longueur_haut: float | None
    longueur_pantalon: float | None
    tour_cuisse: float | None
    tour_genou: float | None
    bas_pantalon: float | None
    entrejambe: float | None
    longueur_robe: float | None

    model_config = ConfigDict(from_attributes=True)