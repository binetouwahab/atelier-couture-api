from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Livraison(Base):
    __tablename__ = "livraisons"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    commande_id: Mapped[int] = mapped_column(
        ForeignKey("commandes.id"),
        unique=True,
        nullable=False
    )

    mode: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    adresse: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    livreur: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    date_prevue: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    date_effective: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    statut: Mapped[str] = mapped_column(
        String(20),
        default="planifiee",
        nullable=False
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )