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
from .globalTypes import DelOwner, DelImage
from .discordTypes import DiscordUserFlags


class DelBotVotes(TypedDict):
    positive: List[str]
    negative: List[str]


class DelBotLinks(TypedDict):
    invite: str
    support: str
    website: str
    donation: str
    repo: str
    privacyPolicy: str


class DelBotSocial(TypedDict):
    twitter: str


class DelBotTheme(TypedDict):
    useCustomColour: bool
    colour: bool
    banner: str


class DelBotWidgetBot(TypedDict):
    channel: str
    options: str
    server: str


class DelBotStatus(TypedDict):
    approved: bool
    premium: bool
    siteBot: bool
    archived: bool


class DelBot(TypedDict):
    _id: str
    clientID: str
    name: str
    prefix: str
    library: str
    tags: List[str]
    vanityUrl: str
    serverCount: int
    shardCount: int
    inServer: Optional[bool]
    token: str
    flags: DiscordUserFlags
    shortDesc: str
    longDesc: str
    modNotes: str
    editors: List[str]
    owner: DelOwner
    avatar: DelImage
    votes: DelBotVotes
    links: DelBotLinks
    social: DelBotSocial
    theme: DelBotTheme
    widgetbot: DelBotWidgetBot
    status: DelBotStatus
