from typing import List

from wulaisdk.response import BaseModel


class Entity(BaseModel):
    # todo: type
    idx_end: int
    name: str
    idx_start: int
    value: str
    seg_value: str
    type: str
    desc: str

    def __init__(self, idx_end: int, name: str, idx_start: int, value: str, seg_value: str,
                 type: str, desc: str) -> None:
        self.idx_end = idx_end
        self.name = name
        self.idx_start = idx_start
        self.value = value
        self.seg_value = seg_value
        self.type = type
        self.desc = desc


class QA(BaseModel):
    knowledge_id: int
    standard_question: str
    question: str

    def __init__(self, knowledge_id: int, standard_question: str, question: str) -> None:
        self.knowledge_id = knowledge_id
        self.standard_question = standard_question
        self.question = question


class ChitChat(BaseModel):
    corpus: str

    def __init__(self, corpus: str) -> None:
        self.corpus = corpus


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
        self.entities = [Entity(**entity) for entity in entities]
        self.task_name = task_name
        self.robot_id = robot_id


class KeyWord(BaseModel):
    keyword_id: int
    keyword: str

    def __init__(self, keyword_id: int, keyword: str) -> None:
        self.keyword_id = keyword_id
        self.keyword = keyword


class Bot(BaseModel):

    def __init__(self, **kwargs) -> None:
        if "qa" in kwargs:
            self.qa = QA(**kwargs.get("qa"))
        elif "chitchat" in kwargs:
            self.chit_chat = ChitChat(**kwargs.get("chitchat"))
        elif "task" in kwargs:
            self.task = Task(**kwargs.get("task"))
        elif "keyword" in kwargs:
            self.keyword = KeyWord(**kwargs.get("keyword"))
        else:
            raise ValueError("err bot body value")
