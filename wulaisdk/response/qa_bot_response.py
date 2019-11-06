from typing import List
from wulaisdk.response import BaseModel
from wulaisdk.response.msg_body import MsgBody
from wulaisdk.response.bot import Bot


class QA(BaseModel):
    knowledge_id: int
    standard_question: str
    question: str

    def __init__(self, knowledge_id: int, standard_question: str, question: str) -> None:
        self.knowledge_id = knowledge_id
        self.standard_question = standard_question
        self.question = question


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
    answer_id: int

    def __init__(self, msg_body: MsgBody, similar_response: List[SimilarResponse], enable_evaluate: bool,
                 delay_ts: int, extra: str, answer_id: int) -> None:
        self.msg_body = MsgBody.from_dict(msg_body)
        self.similar_response = [SimilarResponse.from_dict(sr) for sr in similar_response]
        self.enable_evaluate = enable_evaluate
        self.delay_ts = delay_ts
        self.extra = extra
        self.answer_id = answer_id


class QASuggestedResponse(BaseModel):
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


class QABotResponse(BaseModel):
    is_dispatch: bool
    msg_id: str
    qa_suggested_response: List[QASuggestedResponse]
    extra: str

    def __init__(self, is_dispatch: bool, msg_id: str, qa_suggested_response: List[QASuggestedResponse], extra: str) -> None:
        self.is_dispatch = is_dispatch
        self.msg_id = msg_id
        self.qa_suggested_response = [QASuggestedResponse.from_dict(qsr) for qsr in qa_suggested_response]
        self.extra = extra
