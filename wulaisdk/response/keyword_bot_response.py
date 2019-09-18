from typing import List
from wulaisdk.response import BaseModel
from wulaisdk.response.msg_body import MsgBody
from wulaisdk.response.bot import Bot


class Keyword(BaseModel):
    keyword_id: int
    keyword: str

    def __init__(self, keyword_id: int, keyword: str) -> None:
        self.keyword_id = keyword_id
        self.keyword = keyword


class SimilarResponse:
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


class KeywordSuggestedResponse(BaseModel):
    is_send: bool
    score: int
    response: List[Response]
    keyword: Keyword
    quick_reply: List[str]

    def __init__(self, is_send: bool, score: int, response: List[Response], keyword: Keyword, quick_reply: List[str]) -> None:
        self.is_send = is_send
        self.score = score
        self.response = [Response(**r) for r in response]
        self.keyword = Keyword(**keyword)
        self.quick_reply = quick_reply


class KeywordBotResponse(BaseModel):
    is_dispatch: bool
    msg_id: str
    keyword_suggested_response: List[KeywordSuggestedResponse]

    def __init__(self, is_dispatch: bool, msg_id: str, keyword_suggested_response: List[KeywordSuggestedResponse]) -> None:
        self.is_dispatch = is_dispatch
        self.msg_id = msg_id
        self.keyword_suggested_response = [KeywordSuggestedResponse(**ksr) for ksr in keyword_suggested_response]
