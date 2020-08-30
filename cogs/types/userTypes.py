from typing import TypedDict, List
from .globalTypes import DelImage
from .discordTypes import DiscordUserFlags
from .userStaffTrackingTypes import DelStaffTracking


class DelUserPreferences(TypedDict):
    customGlobalCss: str
    defaultColour: str
    defaultForegroundColour: str
    enableGames: bool
    experiments: bool
    theme: int


class DelUserProfileLinks(TypedDict):
    website: str
    github: str
    gitlab: str
    twitter: str
    instagram: str
    snapchat: str


class DelUserProfile(TypedDict):
    bio: str
    css: str
    links: DelUserProfileLinks


class DelUserGameSnakes(TypedDict):
    maxScore: int


class DelUserGame(TypedDict):
    snakes: DelUserGameSnakes


class DelUserRank(TypedDict):
    admin: bool
    assistant: bool
    mod: bool
    premium: bool
    tester: bool
    translator: bool
    covid: bool


class DelUser(TypedDict):
    _id: str
    token: str
    name: str
    discrim: str
    fullUsername: str
    locale: str
    flags: DiscordUserFlags
    avatar: DelImage
    preferences: DelUserPreferences
    profile: DelUserProfile
    game: DelUserGame
    rank: DelUserRank
    staffTracking: DelUserStaffTracking
