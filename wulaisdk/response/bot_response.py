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
        self.detail = Bot(**detail)


class Response(BaseModel):
    msg_body: MsgBody
    similar_response: List[SimilarResponse]
    enable_evaluate: bool
    delay_ts: int

    def __init__(self, msg_body: MsgBody, similar_response: List[SimilarResponse], enable_evaluate: bool, delay_ts: int) -> None:
        self.msg_body = MsgBody(**msg_body)
        self.similar_response = [SimilarResponse(**sr) for sr in similar_response]
        self.enable_evaluate = enable_evaluate
        self.delay_ts = delay_ts


class SuggestedResponse(BaseModel):
    is_send: bool
    bot: Bot
    source: str
    score: int
    response: List[Response]
    quick_reply: List[str]

    def __init__(self, is_send: bool, bot: Bot, source: str, score: int, response: List[Response], quick_reply: List[str]) -> None:
        self.is_send = is_send
        self.bot = Bot(**bot)
        self.source = source
        self.score = score
        self.response = [Response(**r) for r in response]
        self.quick_reply = quick_reply


class BotResponse(BaseModel):
    is_dispatch: bool
    suggested_response: List[SuggestedResponse]
    msg_id: str

    def __init__(self, is_dispatch: bool, suggested_response: List[SuggestedResponse], msg_id: str) -> None:
        self.is_dispatch = is_dispatch
        self.suggested_response = [SuggestedResponse(**sr) for sr in suggested_response]
        self.msg_id = msg_id
