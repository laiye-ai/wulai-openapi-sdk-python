from typing import List

from wulaisdk.response import BaseModel
from wulaisdk.response.bot import Bot, Response


class SuggestedResponse(BaseModel):
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
    is_dispatch: bool
    suggested_response: List[SuggestedResponse]
    msg_id: str
    extra: str

    def __init__(self, is_dispatch: bool, suggested_response: List[SuggestedResponse], msg_id: str, extra: str) -> None:
        self.is_dispatch = is_dispatch
        self.suggested_response = [SuggestedResponse.from_dict(sr) for sr in suggested_response]
        self.msg_id = msg_id
        self.extra = extra
