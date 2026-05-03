from uuid import UUID
from typing import Optional
from datetime import datetime, date, timezone
from zoneinfo import ZoneInfo
from utils import get_supabase_client
from models import Person, Patient, CalendarEvent

# Eastern Time (handles both EST and EDT automatically)
EASTERN_TZ = ZoneInfo("America/New_York")


def list_people(user_id: UUID) -> list[Person]:
    data = (
        get_supabase_client()
        .table("person")
        .select("*")
        .eq("user_id", str(user_id))
        .execute()
        .data
    )

    # Parse datetime strings from Supabase
    people = []
    for row in data:
        if row.get("created_at") and isinstance(row.get("created_at"), str):
            row["created_at"] = datetime.fromisoformat(row["created_at"].replace('Z', '+00:00'))
        people.append(Person(**row))

    return people


def list_people_by_alias(user_id: UUID, alias: str) -> list[Person]:
    data = (
        get_supabase_client()
        .table("person")
        .select("*")
        .eq("user_id", str(user_id))
        .contains("aliases", [alias])
        .execute()
        .data
    )

    # Parse datetime strings from Supabase
    people = []
    for row in data:
        if row.get("created_at") and isinstance(row.get("created_at"), str):
            row["created_at"] = datetime.fromisoformat(row["created_at"].replace('Z', '+00:00'))
        people.append(Person(**row))

    return people


def get_patient(user_id: UUID) -> Optional[Patient]:
    data = (
        get_supabase_client()
        .table("patients")
        .select("*")
        .eq("user_id", str(user_id))
        .execute()
        .data
    )
    if not data:
        return None

    # Parse datetime/date strings from Supabase
    row = data[0]
    if row.get("date_of_birth") and isinstance(row.get("date_of_birth"), str):
        row["date_of_birth"] = date.fromisoformat(row["date_of_birth"])
    if row.get("created_at") and isinstance(row.get("created_at"), str):
        row["created_at"] = datetime.fromisoformat(row["created_at"].replace('Z', '+00:00'))
    if row.get("updated_at") and isinstance(row.get("updated_at"), str):
        row["updated_at"] = datetime.fromisoformat(row["updated_at"].replace('Z', '+00:00'))

    return Patient(**row)


def get_today_calendar_events(user_id: UUID) -> list[CalendarEvent]:
    """Get all calendar events for today for the given user (in Eastern Time)."""
    # Get today's date range in Eastern Time
    now_eastern = datetime.now(EASTERN_TZ)
    today_start = now_eastern.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start.replace(hour=23, minute=59, second=59, microsecond=999999)

    data = (
        get_supabase_client()
        .table("calendar_events")
        .select("*")
        .eq("user_id", str(user_id))
        .gte("start_time", today_start.isoformat())
        .lte("start_time", tomorrow_start.isoformat())
        .order("start_time", desc=False)
        .execute()
        .data
    )

    # Parse datetime strings from Supabase (stored in UTC)
    events = []
    for row in data:
        if isinstance(row.get("start_time"), str):
            row["start_time"] = datetime.fromisoformat(row["start_time"].replace('Z', '+00:00'))
        if row.get("end_time") and isinstance(row.get("end_time"), str):
            row["end_time"] = datetime.fromisoformat(row["end_time"].replace('Z', '+00:00'))
        if row.get("created_at") and isinstance(row.get("created_at"), str):
            row["created_at"] = datetime.fromisoformat(row["created_at"].replace('Z', '+00:00'))
        if row.get("updated_at") and isinstance(row.get("updated_at"), str):
            row["updated_at"] = datetime.fromisoformat(row["updated_at"].replace('Z', '+00:00'))
        events.append(CalendarEvent(**row))

    return events
