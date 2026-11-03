from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LigneCommande(Base):
    __tablename__ = "lignes_commande"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    commande_id: Mapped[int] = mapped_column(
        ForeignKey("commandes.id"),
        nullable=False
    )

    type_vetement_id: Mapped[int] = mapped_column(
        ForeignKey("types_vetement.id"),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    quantite: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    prix_unitaire: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )