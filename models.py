from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import (
    Text,
    text,
    Enum,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID, TIMESTAMP
from datetime import datetime
from typing import Optional
import uuid
import enum


class RelationshipEnum(str, enum.Enum):
    spouse = "spouse"
    parent = "parent"
    child = "child"
    sibling = "sibling"
    friend = "friend"
    caregiver = "caregiver"
    neighbor = "neighbor"
    dad = "dad"
    mom = "mom"
    son = "son"
    daughter = "daughter"
    husband = "husband"
    wife = "wife"


class Base(DeclarativeBase):
    pass


class Person(Base):
    __tablename__ = "person"
    __table_args__ = {"schema": "public"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    relationship: Mapped[str] = mapped_column(
        Enum(RelationshipEnum, name="relationship", schema="public", create_type=False),
        nullable=False,
    )
    aliases: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        nullable=False,
        server_default="{}",
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
