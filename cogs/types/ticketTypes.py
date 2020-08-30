# Discord Extreme List - Discord's unbiased list.

# Copyright (C) 2020 Cairo Mitchell-Acason

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
