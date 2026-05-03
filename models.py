from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import (
    Text,
    text,
    Enum,
    Date,
    Boolean,
    Integer,
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


class EventTypeEnum(str, enum.Enum):
    appointment = "appointment"
    medication = "medication"
    activity = "activity"
    reminder = "reminder"
    meal = "meal"
    visit = "visit"


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


class CalendarEvent(Base):
    __tablename__ = "calendar_events"
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
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_type: Mapped[str] = mapped_column(
        Enum(EventTypeEnum, name="event_type", schema="public", create_type=False),
        nullable=False,
    )
    start_time: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        index=True,
    )
    end_time: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
    all_day: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        server_default="false",
    )
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    person_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )
    recurrence_rule: Mapped[str | None] = mapped_column(Text, nullable=True)
    reminder_minutes: Mapped[list[int] | None] = mapped_column(
        ARRAY(Integer),
        nullable=True,
    )
    completed: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        server_default="false",
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
