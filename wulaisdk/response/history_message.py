from typing import List
from wulaisdk.response import BaseModel
from wulaisdk.response.msg_body import MsgBody


class SenderInfo(BaseModel):
    avatar_url: str
    nickname: str
    real_name: str

    def __init__(self, avatar_url: str, nickname: str, real_name: str) -> None:
        self.avatar_url = avatar_url
        self.nickname = nickname
        self.real_name = real_name


class UserInfo(BaseModel):
    avatar_url: str
    nickname: str

    def __init__(self, avatar_url: str, nickname: str) -> None:
        self.avatar_url = avatar_url
        self.nickname = nickname


class Msg(BaseModel):
    direction: str
    sender_info: SenderInfo
    msg_type: str
    extra: str
    msg_id: str
    msg_ts: str
    user_info: UserInfo
    msg_body: MsgBody

    def __init__(self, direction: str, sender_info: SenderInfo, msg_type: str, extra: str, msg_id: str, msg_ts: str, user_info: UserInfo, msg_body: MsgBody) -> None:
        self.direction = direction
        if sender_info:
            self.sender_info = SenderInfo(**sender_info)
        else:
            self.sender_info = SenderInfo("", "", "")
        self.msg_type = msg_type
        self.extra = extra
        self.msg_id = msg_id
        self.msg_ts = msg_ts
        if user_info:
            self.user_info = UserInfo(**user_info)
        else:
            self.user_info = UserInfo("", "")
        self.msg_body = MsgBody(**msg_body)


class HistoryMessage(BaseModel):
    msg: List[Msg]
    has_more: bool

    def __init__(self, msg: List[Msg], has_more: bool) -> None:
        self.msg = [Msg(**m) for m in msg]
        self.has_more = has_more
