from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TypeVetement(Base):
    __tablename__ = "types_vetement"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    nom: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    prix_base: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    delai_jours: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    actif: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )