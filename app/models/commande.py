from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Commande(Base):
    __tablename__ = "commandes"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    numero: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False
    )

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id"),
        nullable=False
    )

    mesure_id: Mapped[int | None] = mapped_column(
        ForeignKey("mesures.id"),
        nullable=True
    )

    statut: Mapped[str] = mapped_column(
        String(20),
        default="en_attente",
        nullable=False
    )

    date_commande: Mapped[date] = mapped_column(
        Date,
        default=date.today,
        nullable=False
    )

    date_livraison_prevue: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    date_livraison_reelle: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    remise: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    montant_total: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    montant_paye: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    cree_par_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateurs.id"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    lignes: Mapped[list["LigneCommande"]] = relationship(
    back_populates="commande",
    cascade="all, delete-orphan"
)