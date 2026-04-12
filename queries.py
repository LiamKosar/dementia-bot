from uuid import UUID
from typing import Optional
from utils import get_supabase_client
from models import Person, Patient


def list_people(user_id: UUID) -> list[Person]:
    data = (
        get_supabase_client()
        .table("person")
        .select("*")
        .eq("user_id", str(user_id))
        .execute()
        .data
    )
    return [Person(**row) for row in data]


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
    return [Person(**row) for row in data]


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
    return Patient(**data[0])
