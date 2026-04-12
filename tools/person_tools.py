import asyncio
import json
from uuid import UUID

from pipecat.adapters.schemas.function_schema import FunctionSchema
from pipecat.frames.frames import OutputTransportMessageFrame
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.services.llm_service import FunctionCallParams

from models import Person, Patient
from queries import list_people, list_people_by_alias, get_patient
from context import session_context
from loguru import logger


def _lookup_person_schema(people: list[Person]) -> FunctionSchema:
    aliases: set[str] = set()
    for person in people:
        aliases.update(person.aliases or [])
    alias_param: dict = {
        "type": "string",
        "description": "The alias or name of the person to look up. A PERSON CAN HAVE MULTIPLE ALIASES - CHOOSE THE ALIAS MOST FITTING TO WHAT THE USER IS ASKING ABOUT.",
    }
    if aliases:
        alias_param["enum"] = sorted(aliases)
    return FunctionSchema(
        name="lookup_person",
        description="Look up information about a person by their alias.",
        properties={"alias": alias_param},
        required=["alias"],
    )


def _show_patient_schema() -> FunctionSchema:
    return FunctionSchema(
        name="show_patient",
        description="Use if patient asks about themselves. Show detailed information about the patient, including their date of birth, occupations, nicknames, and other biographical details. Will show a photo of the patient.",
        properties={},
        required=[],
    )


def _person_tool_schemas(people: list[Person]) -> list[FunctionSchema]:
    """Build all person-related tool schemas. Each tool decides what it needs from people."""
    return [
        _lookup_person_schema(people),
        _show_patient_schema(),
    ]


async def build_person_tools(user_id: UUID) -> list[FunctionSchema]:
    """Fetch people once and build all person-related tool schemas. Single DB query."""
    people = list_people(user_id)
    return _person_tool_schemas(people)


async def _send_image_via_app_message(image_url: str) -> None:
    """Send image path to client via Daily app message."""
    session = session_context.get()
    if not session or not session.transport:
        logger.warning("No session or transport available to send image message")
        return

    message = OutputTransportMessageFrame({"type": "image", "path": image_url})

    try:
        await session.transport._client.send_message(message)
        logger.info(f"Sent image app message: {image_url}")
    except Exception as e:
        logger.error(f"Failed to send image app message: {e}")


async def handle_lookup_person(params: FunctionCallParams):
    session = session_context.get()
    if not session:
        raise RuntimeError("No session context; user_id unavailable")

    alias = params.arguments["alias"]
    logger.info(f"Looking up person: {alias}")
    people: list[Person] = list_people_by_alias(session.user_id, alias)
    logger.info(f"Found people: {people}")
    if people and people[0].image_url:
        logger.info(f"Sending person image via app message: {people[0].image_url}")
        asyncio.create_task(_send_image_via_app_message(people[0].image_url))

    if len(people) == 0:
        result = "The patient does not not have a record of a person with this alias."
    else:
        people_data = [_person_to_dict(p) for p in people]
        result = json.dumps(people_data, indent=2)
    await params.result_callback(result)


async def handle_show_patient(params: FunctionCallParams):
    session = session_context.get()
    if not session:
        raise RuntimeError("No session context; user_id unavailable")

    logger.info("Showing patient information")
    patient: Patient | None = get_patient(session.user_id)

    if not patient:
        result = "No patient information found for this user."
    else:
        if patient.photo_url:
            logger.info(f"Sending patient image via app message: {patient.photo_url}")
            asyncio.create_task(_send_image_via_app_message(patient.photo_url))

        patient_data = _patient_to_dict(patient)
        result = json.dumps(patient_data, indent=2)

    await params.result_callback(result)


def _person_to_dict(person: Person) -> dict:
    # Handle both enum and string values for relationship
    relationship = person.relationship
    if hasattr(relationship, "value"):
        relationship = relationship.value

    return {
        "full_name": person.full_name,
        "relationship": str(relationship),
        "aliases": person.aliases or [],
        "notes": person.notes,
    }


def _patient_to_dict(patient: Patient) -> dict:
    # Handle date_of_birth - Supabase returns it as string, not date object
    dob = patient.date_of_birth
    if dob and hasattr(dob, "isoformat"):
        dob = dob.isoformat()

    return {
        "full_name": patient.full_name,
        "nicknames": patient.nicknames or [],
        "date_of_birth": dob,
        "birth_location": patient.birth_location,
        "current_occupation": patient.current_occupation,
        "past_occupations": patient.past_occupations or [],
        "gender": patient.gender,
        "preferred_language": patient.preferred_language,
        "notes": patient.notes,
    }
