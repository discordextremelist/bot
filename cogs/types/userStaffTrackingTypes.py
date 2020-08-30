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

from typing import TypedDict, List, Optional


class DelStaffTrackingDetailsAway(TypedDict):
    status: bool
    message: str


class DelStaffTrackingDetails(TypedDict):
    away: DelStaffTrackingDetailsAway
    standing: str
    country: str
    timezone: str
    managementNotes: str
    languages: List[str]


class DelStaffTrackingLastAccessed(TypedDict):
    time: int
    page: str


class DelStaffTrackingPunishmentsSub(TypedDict):
    executorName: Optional[str]
    executor: str
    reason: str
    date: int


class DelStaffTrackingPunishmentsStrike(DelStaffTrackingPunishmentsSub):
    pass


class DelStaffTrackingPunishmentsWarning(DelStaffTrackingPunishmentsSub):
    pass


class DelStaffTrackingPunishments(TypedDict):
    strikes: DelStaffTrackingPunishmentsStrike
    warnings: DelStaffTrackingPunishmentsWarning


class DelStaffTrackingHandledSub(TypedDict):
    total: int
    approved: int
    unapprove: Optional[int]
    declined: int
    remove: int


class DelStaffTrackingHandled(TypedDict):
    allTime: DelStaffTrackingHandledSub
    prevWeek: DelStaffTrackingHandledSub
    thisWeek: DelStaffTrackingHandledSub


class DelStaffTracking(TypedDict):
    details: DelStaffTrackingDetails
    lastLogin: int
    lastAccessed: DelStaffTrackingLastAccessed
    punishments: DelStaffTrackingPunishments
    handledBots: DelStaffTrackingHandled
    handledServers: DelStaffTrackingHandled
    handledTemplates: DelStaffTrackingHandled
