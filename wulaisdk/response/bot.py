from typing import List

from wulaisdk.response import BaseModel
from wulaisdk.response.msg_body import MsgBody


class Entity(BaseModel):
    """
    抽取的实体
    """
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


class ChitChat(BaseModel):
    """
    闲聊机器人
    """
    corpus: str

    def __init__(self, corpus: str) -> None:
        self.corpus = corpus


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


class KeyWord(BaseModel):
    """
    关键字机器人
    """
    keyword_id: int
    keyword: str

    def __init__(self, keyword_id: int, keyword: str) -> None:
        self.keyword_id = keyword_id
        self.keyword = keyword


class Bot(BaseModel):
    """
    当前触发的机器人，如果机器人回复兜底内容，则bot为空
    """

    def __init__(self, **kwargs) -> None:
        if "qa" in kwargs:
            self.qa = QA.from_dict(kwargs.get("qa"))
        elif "chitchat" in kwargs:
            self.chit_chat = ChitChat.from_dict(kwargs.get("chitchat"))
        elif "task" in kwargs:
            self.task = Task.from_dict(kwargs.get("task"))
        elif "keyword" in kwargs:
            self.keyword = KeyWord.from_dict(kwargs.get("keyword"))
        else:
            for k, v in kwargs:
                setattr(self, k, v)
            # raise ValueError("err bot body value")


class SimilarResponse(BaseModel):
    """
    机器人平台手动或自动配置的推荐知识点，在机器人平台-知识库-知识点详情配置。
    """
    url: str
    source: str
    detail: Bot

    def __init__(self, url: str, source: str, detail: Bot) -> None:
        self.url = url
        self.source = source
        self.detail = Bot.from_dict(detail)


class Response(BaseModel):
    """
    单条回复内容
    """
    msg_body: MsgBody
    similar_response: List[SimilarResponse]
    enable_evaluate: bool
    delay_ts: int
    extra: str
    answer_id: int

    def __init__(self, msg_body: MsgBody, similar_response: List[SimilarResponse], enable_evaluate: bool,
                 delay_ts: int, extra: str, answer_id: int) -> None:
        self.msg_body = MsgBody.from_dict(msg_body)
        self.similar_response = [SimilarResponse.from_dict(sr) for sr in similar_response]
        self.enable_evaluate = enable_evaluate
        self.delay_ts = delay_ts
        self.extra = extra
        self.answer_id = answer_id

