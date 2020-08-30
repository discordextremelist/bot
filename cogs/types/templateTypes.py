from typing import TypedDict, List
from .globalTypes import DelOwner, DelImage
from .discordTypes import DiscordRole, DiscordChannel


class DelTemplateLinks(TypedDict):
    linkToServerPage: bool
    template: str


class DelTemplate(TypedDict):
    _id: str
    name: str
    region: str
    locale: str
    afkTimeout: int
    verificationLevel: int
    defaultMessageNotifications: int
    explicitContent: int
    roles: List[DiscordRole]
    channels: List[DiscordChannel]
    usageCount: int
    shortDesc: str
    longDesc: str
    tags: List[str]
    fromGuild: str
    owner: DelOwner
    icon: DelImage
    links: DelTemplateLinks
