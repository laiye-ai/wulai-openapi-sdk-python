"""
对话类
1. 获取机器人回复
2. 获取关键字机器人回复
3. 获取问答机器人回复
4. 获取任务机器人回复
5. 同步发给用户的消息
6. 接收用户发的消息
7. 查询历史消息
8. 给用户发消息
9. 获取用户输入联想
"""
from typing import List

from wulaisdk.response import BaseModel

from wulaisdk.response.bot import Bot, Response
from wulaisdk.response.msg_body import MsgBody


class SenderInfo(BaseModel):
    """
    消息发出者信息，可以是人工或机器人
    """
    avatar_url: str
    nickname: str
    real_name: str

    def __init__(self, avatar_url: str, nickname: str, real_name: str) -> None:
        self.avatar_url = avatar_url
        self.nickname = nickname
        self.real_name = real_name


class UserInfo(BaseModel):
    """
    用户信息
    """
    avatar_url: str
    nickname: str

    def __init__(self, avatar_url: str, nickname: str) -> None:
        self.avatar_url = avatar_url
        self.nickname = nickname


class Msg(BaseModel):
    """
    返回的单条消息
    """
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


class Keyword(BaseModel):
    """
    关键字机器人
    """
    keyword_id: int
    keyword: str

    def __init__(self, keyword_id: int, keyword: str) -> None:
        self.keyword_id = keyword_id
        self.keyword = keyword


class KeywordSuggestedResponse(BaseModel):
    """
    单条关键字机器人应答回复
    """
    is_send: bool
    score: int
    response: List[Response]
    keyword: Keyword
    quick_reply: List[str]

    def __init__(self, is_send: bool, score: int, response: List[Response], keyword: Keyword, quick_reply: List[str]) -> None:
        self.is_send = is_send
        self.score = score
        self.response = [Response.from_dict(r) for r in response]
        self.keyword = Keyword.from_dict(keyword)
        self.quick_reply = quick_reply


class QA(BaseModel):
    """
    问答机器人
    """
    knowledge_id: int
    standard_question: str
    question: str

    def __init__(self, knowledge_id: int, standard_question: str, question: str) -> None:
        self.knowledge_id = knowledge_id
        self.standard_question = standard_question
        self.question = question


class QASuggestedResponse(BaseModel):
    """
    单条问答机器人应答回复
    """
    qa: QA
    is_send: bool
    score: int
    response: List[Response]
    quick_reply: List[str]

    def __init__(self, qa: QA, is_send: bool, score: int, response: List[Response], quick_reply: List[str]) -> None:
        self.qa = QA.from_dict(qa)
        self.is_send = is_send
        self.score = score
        self.response = [Response.from_dict(r) for r in response]
        self.quick_reply = quick_reply


class Entity(BaseModel):
    """
    抽取的实体列表
    """
    idx_end: int
    name: str
    idx_start: int
    value: str
    seg_value: str
    type: str
    desc: str

    def __init__(self, idx_end: int, name: str, idx_start: int, value: str, seg_value: str, type: str, desc: str) -> None:
        self.idx_end = idx_end
        self.name = name
        self.idx_start = idx_start
        self.value = value
        self.seg_value = seg_value
        self.type = type
        self.desc = desc


class Task(BaseModel):
    """
    任务机器人
    """
    block_type: str
    block_id: int
    task_id: int
    block_name: str
    entities: List[Entity]
    task_name: str
    robot_id: int

    def __init__(self, block_type: str, block_id: int, task_id: int, block_name: str, entities: List[Entity],
                 task_name: str, robot_id: int) -> None:
        self.block_type = block_type
        self.block_id = block_id
        self.task_id = task_id
        self.block_name = block_name
        self.entities = [Entity.from_dict(entity) for entity in entities]
        self.task_name = task_name
        self.robot_id = robot_id


class TaskSuggestedResponse(BaseModel):
    """
    单条任务机器人应答回复
    """
    score: int
    is_send: bool
    task: Task
    response: List[Response]
    quick_reply: List[str]

    def __init__(self, score: int, is_send: bool, task: Task, response: List[Response], quick_reply: List[str]) -> None:
        self.score = score
        self.is_send = is_send
        self.task = Task.from_dict(task)
        self.response = [Response.from_dict(r) for r in response]
        self.quick_reply = quick_reply


class SuggestedResponse(BaseModel):
    """
    单条机器人应答回复
    """
    is_send: bool
    bot: Bot
    source: str
    score: int
    response: List[Response]
    quick_reply: List[str]

    def __init__(self, is_send: bool, bot: Bot, source: str, score: int, response: List[Response], quick_reply: List[str]) -> None:
        self.is_send = is_send
        self.bot = Bot.from_dict(bot)
        self.source = source
        self.score = score
        self.response = [Response.from_dict(r) for r in response]
        self.quick_reply = quick_reply


class BotResponse(BaseModel):
    """
    获取机器人回复
    """
    is_dispatch: bool
    suggested_response: List[SuggestedResponse]
    msg_id: str
    extra: str

    def __init__(self, is_dispatch: bool, suggested_response: List[SuggestedResponse], msg_id: str, extra: str) -> None:
        self.is_dispatch = is_dispatch
        self.suggested_response = [SuggestedResponse.from_dict(sr) for sr in suggested_response]
        self.msg_id = msg_id
        self.extra = extra


class KeywordBotResponse(BaseModel):
    """
    获取关键字机器人回复
    """
    is_dispatch: bool
    msg_id: str
    keyword_suggested_response: List[KeywordSuggestedResponse]
    extra: str

    def __init__(self, is_dispatch: bool, msg_id: str, keyword_suggested_response: List[KeywordSuggestedResponse], extra: str) -> None:
        self.is_dispatch = is_dispatch
        self.msg_id = msg_id
        self.keyword_suggested_response = [KeywordSuggestedResponse.from_dict(ksr) for ksr in keyword_suggested_response]
        self.extra = extra


class QABotResponse(BaseModel):
    """
    获取问答机器人回复
    """
    is_dispatch: bool
    msg_id: str
    qa_suggested_response: List[QASuggestedResponse]
    extra: str

    def __init__(self, is_dispatch: bool, msg_id: str, qa_suggested_response: List[QASuggestedResponse], extra: str) -> None:
        self.is_dispatch = is_dispatch
        self.msg_id = msg_id
        self.qa_suggested_response = [QASuggestedResponse.from_dict(qsr) for qsr in qa_suggested_response]
        self.extra = extra


class TaskBotResponse(BaseModel):
    """
    获取任务机器人回复
    """
    is_dispatch: bool
    msg_id: str
    task_suggested_response: List[TaskSuggestedResponse]
    extra: str

    def __init__(self, is_dispatch: bool, msg_id: str, task_suggested_response: List[TaskSuggestedResponse], extra: str) -> None:
        self.is_dispatch = is_dispatch
        self.msg_id = msg_id
        self.task_suggested_response = [TaskSuggestedResponse.from_dict(tsr) for tsr in task_suggested_response]
        self.extra = extra


class SyncMessage(BaseModel):
    """
    同步发给用户的消息
    """
    msg_id: str

    def __init__(self, msg_id: str) -> None:
        self.msg_id = msg_id


class ReceiveMessage(BaseModel):
    """
    接收用户发的消息
    """
    msg_id: str

    def __init__(self, msg_id: str) -> None:
        self.msg_id = msg_id


class HistoryMessage(BaseModel):
    """
    查询历史消息
    """
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


