from typing import List

from wulaisdk.response import BaseModel
from wulaisdk.response.bot import Response


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
