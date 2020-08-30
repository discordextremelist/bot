from typing import TypedDict, Optional
from enum import Enum


class DelTicketIds(TypedDict):
    channel: str
    message: str
    log: str
    bot: str
    history: Optional[str]


class DelTicketStatus(Enum):
    AwaitingResponse = 0
    AwaitingFixes = 1
    Closed = 2


class DelTicket(TypedDict):
    _id: str
    ids: DelTicketIds
    status: DelTicketStatus
    closureReason: Optional[str]
