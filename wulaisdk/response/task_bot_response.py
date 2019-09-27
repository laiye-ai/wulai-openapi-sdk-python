from typing import List
from wulaisdk.response import BaseModel
from wulaisdk.response.msg_body import MsgBody
from wulaisdk.response.bot import Bot


class SimilarResponse(BaseModel):
    url: str
    source: str
    detail: Bot

    def __init__(self, url: str, source: str, detail: Bot) -> None:
        self.url = url
        self.source = source
        self.detail = Bot.from_dict(detail)


class Response(BaseModel):
    msg_body: MsgBody
    similar_response: List[SimilarResponse]
    enable_evaluate: bool
    delay_ts: int
    extra: str

    def __init__(self, msg_body: MsgBody, similar_response: List[SimilarResponse], enable_evaluate: bool,
                 delay_ts: int, extra: str) -> None:
        self.msg_body = MsgBody.from_dict(msg_body)
        self.similar_response = [SimilarResponse.from_dict(sr) for sr in similar_response]
        self.enable_evaluate = enable_evaluate
        self.delay_ts = delay_ts
        self.extra = extra


class Entity(BaseModel):
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


class TaskBotResponse(BaseModel):
    is_dispatch: bool
    msg_id: str
    task_suggested_response: List[TaskSuggestedResponse]
    extra: str

    def __init__(self, is_dispatch: bool, msg_id: str, task_suggested_response: List[TaskSuggestedResponse], extra: str) -> None:
        self.is_dispatch = is_dispatch
        self.msg_id = msg_id
        self.task_suggested_response = [TaskSuggestedResponse.from_dict(tsr) for tsr in task_suggested_response]
        self.extra = extra
