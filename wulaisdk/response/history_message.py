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
            self.sender_info = SenderInfo.from_dict(sender_info)
        else:
            self.sender_info = SenderInfo("", "", "")
        self.msg_type = msg_type
        self.extra = extra
        self.msg_id = msg_id
        self.msg_ts = msg_ts
        if user_info:
            self.user_info = UserInfo.from_dict(user_info)
        else:
            self.user_info = UserInfo("", "")
        self.msg_body = MsgBody.from_dict(msg_body)


class HistoryMessage(BaseModel):
    msg: List[Msg]
    has_more: bool

    def __init__(self, msg: List[Msg], has_more: bool) -> None:
        self.msg = [Msg.from_dict(m) for m in msg]
        self.has_more = has_more


class SendMessage(BaseModel):
    """
    给用户发消息
    """
    msg_id: str

    def __init__(self, msg_id: str) -> None:
        self.msg_id = msg_id


class UserSuggestion(BaseModel):
    """
    输入联想内容。在相同对话类型中，如有多条联想内容，按照置信度从高到低排序；在不同对话类型中，如有任务对话的联想，则不返回问答对话的联想内容。
    """
    suggestion: str

    def __init__(self, suggestion: str) -> None:
        self.suggestion = suggestion


class GetUserSuggestion(BaseModel):
    """
    获取用户输入联想
    """
    user_suggestions: List[UserSuggestion]

    def __init__(self, user_suggestions: List[UserSuggestion]) -> None:
        self.user_suggestions = [UserSuggestion.from_dict(user_suggestion) for user_suggestion in user_suggestions]
