from typing import TypedDict, List, Optional
from enum import Enum


class DiscordUserFlags(Enum):
    Nil = 0
    DiscordEmployee = 1
    DiscordPartner = 2
    DiscordHypeSquadEvents = 4
    BugHunterLevel1 = 8
    HypeSquadHouseBravery = 64
    HypeSquadHouseBrilliance = 128
    HypeSquadHouseBalance = 256
    EarlySupporter = 512
    TeamUser = 1024
    System = 4096
    BugHunterLevel2 = 16384
    VerifiedBot = 65536
    VerifiedBotDeveloper = 131072


class DiscordUserPremiumType(Enum):
    Nil = 0
    NitroClassic = 1
    Nitro = 2


class DiscordUser(TypedDict):
    id: str
    username: str
    discriminator: str
    avatar: str
    bot: Optional[bool]
    system: Optional[bool]
    mfa_enabled: Optional[bool]
    locale: Optional[str]
    verified: Optional[bool]
    email: Optional[str]
    flags: Optional[DiscordUserFlags]
    premium_type: DiscordUserPremiumType
    public_flags: Optional[DiscordUserFlags]


class DiscordRoleTags(TypedDict):
    bot_id: Optional[str]
    # premium_subscriber: None
    integration_id: Optional[str]


class DiscordRole(TypedDict):
    id: str
    name: str
    color: int
    hoist: bool
    position: int
    permissions: int  # DEPRECATED - Use permissions_new instead
    permissions_new: str
    managed: bool
    mentionable: bool
    tags: Optional[DiscordRoleTags]


class DiscordPartialChannel(TypedDict):
    id: str
    type: str
    name: str


class DiscordOverwriteTypes(Enum):
    Member = "member"
    Role = "role"


class DiscordOverwrites(TypedDict):
    id: str
    type: DiscordOverwriteTypes
    allow: int  # DEPRECATED - Use allow_new instead
    allow_new: str
    deny: int  # DEPRECATED - Use deny_new instead
    deny_new: str


class DiscordChannel(DiscordPartialChannel):
    guild_id: Optional[str]
    position: int
    permission_overwrites: Optional[List[DiscordOverwrites]]
    topic: Optional[str]
    nsfw: Optional[bool]
    last_message_id: Optional[str]
    bitrate: Optional[int]
    user_limit: Optional[int]
    rate_limit_per_user: Optional[int]
    recipients: Optional[DiscordUser]
    icon: Optional[str]
    owner_id: Optional[str]
    application_id: Optional[str]
    parent_id: Optional[str]
    last_pin_timestamp: Optional[str]
