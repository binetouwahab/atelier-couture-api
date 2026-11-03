from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    nom: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    prenom: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    telephone: Mapped[str] = mapped_column(
        String(21),
        unique=True,
        nullable=False
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    adresse: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    genre: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    notes: Mapped[str | None] = mapped_column(
        String,
        nullable=True
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