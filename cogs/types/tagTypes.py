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

from typing import TypedDict, List, Optional


class DelTagContents(TypedDict):
    en: str
    tr: str
    fr: str
    pt: str


class DelTag(TypedDict):
    _id: str
    creator: str
    creationDate: int
    contents: DelTagContents
    aliases: Optional[List[str]]
