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
