from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import (
    Text,
    text,
    Enum,
    Date,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID, TIMESTAMP, JSONB
from datetime import datetime, date
from typing import Optional, TypedDict
import uuid
import enum


class Address(TypedDict):
    street: str
    city: str
    state: str
    zip: str
    country: str


class Occupation(TypedDict):
    title: str
    company: str
    startYear: str
    endYear: str


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


class Patient(Base):
    __tablename__ = "patients"
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
    nicknames: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        nullable=False,
        server_default="'{}'::text[]",
    )
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    birth_location: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_address: Mapped[Address | None] = mapped_column(JSONB, nullable=True)
    past_addresses: Mapped[list[Address] | None] = mapped_column(
        JSONB,
        nullable=True,
        server_default="'[]'::jsonb",
    )
    current_occupation: Mapped[Occupation | None] = mapped_column(JSONB, nullable=True)
    past_occupations: Mapped[list[Occupation] | None] = mapped_column(
        JSONB,
        nullable=True,
        server_default="'[]'::jsonb",
    )
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    gender: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferred_language: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="'en'::text",
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
