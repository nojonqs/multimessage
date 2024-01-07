from typing import Any, Dict, List, TypedDict


class SignalAccount(TypedDict):
    number: str
    uuid: str


class SignalProfile(TypedDict):
    lastUpdateTimestamp: int
    givenName: str
    familyName: str
    about: str
    aboutEmoji: str
    mobileCoinAddress: str


class SignalContact(TypedDict):
    number: str
    uuid: str
    username: str
    name: str
    profile: SignalProfile


class SignalGroup(TypedDict):
    id: str
    name: str
    description: str
    isMember: bool
    isBlocked: bool
    messageExpirationTime: int
    members: List[SignalAccount]
    pendingMembers: List[SignalAccount]
    requestingMembers: List[SignalAccount]
    admins: List[SignalAccount]
    banned: List[SignalAccount]
    permissionAddMember: str
    permissionEditDetails: str
    permissionSendMessage: str
    groupInviteLink: str


class SignalCliJsonRpcRequest(TypedDict):
    jsonrpc: str
    method: str
    params: Dict[str, Any]
    id: str


class NoPhoneNumberLinked(Exception):
    pass


class SignalCliSocketError(Exception):
    pass