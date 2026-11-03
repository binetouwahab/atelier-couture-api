from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class HistoriqueStatut(Base):
    __tablename__ = "historiques_statut"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    commande_id: Mapped[int] = mapped_column(
        ForeignKey("commandes.id"),
        nullable=False
    )

    ancien_statut: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    nouveau_statut: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    commentaire: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    utilisateur_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateurs.id"),
        nullable=False
    )

    date_changement: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )