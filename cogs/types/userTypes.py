# Discord Extreme List - Discord's unbiased list.

# Copyright (C) 2020-2025 Carolina Mitchell, Advaith Jagathesan, John Burke

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
    staffTracking: DelStaffTracking
