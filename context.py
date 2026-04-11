from contextvars import ContextVar
from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID
from pipecat.transports.daily.transport import DailyTransport

# if TYPE_CHECKING:
#     from pipecat.transports.daily.transport import DailyTransport


@dataclass
class BotSession:
    user_id: UUID
    transport: DailyTransport


session_context: ContextVar[BotSession | None] = ContextVar("bot_session", default=None)
