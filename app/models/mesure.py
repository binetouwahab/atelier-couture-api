from datetime import date

from sqlalchemy import Date, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Mesure(Base):
    __tablename__ = "mesures"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id"),
        nullable=False
    )

    date_prise: Mapped[date] = mapped_column(
        Date,
        default=date.today,
        nullable=False
    )

    prise_par_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateurs.id"),
        nullable=False
    )

    notes: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    taille_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_cou: Mapped[float | None] = mapped_column(Float, nullable=True)
    carrure_dos: Mapped[float | None] = mapped_column(Float, nullable=True)
    longueur_epaule: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_poitrine: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_taille: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_bassin: Mapped[float | None] = mapped_column(Float, nullable=True)
    longueur_manche: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_bras: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_poignet: Mapped[float | None] = mapped_column(Float, nullable=True)
    longueur_dos: Mapped[float | None] = mapped_column(Float, nullable=True)
    longueur_haut: Mapped[float | None] = mapped_column(Float, nullable=True)
    longueur_pantalon: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_cuisse: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_genou: Mapped[float | None] = mapped_column(Float, nullable=True)
    bas_pantalon: Mapped[float | None] = mapped_column(Float, nullable=True)
    entrejambe: Mapped[float | None] = mapped_column(Float, nullable=True)
    longueur_robe: Mapped[float | None] = mapped_column(Float, nullable=True)