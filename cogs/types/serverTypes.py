from typing import TypedDict, List
from .globalTypes import DelOwner, DelImage


class DelServerLinks(TypedDict):
    invite: str
    website: str
    donation: str


class DelServerStatus(TypedDict):
    reviewRequired: bool


class DelServer(TypedDict):
    _id: str
    inviteCode: str
    name: str
    shortDesc: str
    longDesc: str
    tags: List[str]
    previewChannel: str
    owner: DelOwner
    icon: DelImage
    links: DelServerLinks
    status: DelServerStatus
