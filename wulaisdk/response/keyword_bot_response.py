from typing import List

from wulaisdk.response import BaseModel
from wulaisdk.response.bot import Response


class Keyword(BaseModel):
    keyword_id: int
    keyword: str

    def __init__(self, keyword_id: int, keyword: str) -> None:
        self.keyword_id = keyword_id
        self.keyword = keyword


class KeywordSuggestedResponse(BaseModel):
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


class KeywordBotResponse(BaseModel):
    is_dispatch: bool
    msg_id: str
    keyword_suggested_response: List[KeywordSuggestedResponse]
    extra: str

    def __init__(self, is_dispatch: bool, msg_id: str, keyword_suggested_response: List[KeywordSuggestedResponse], extra: str) -> None:
        self.is_dispatch = is_dispatch
        self.msg_id = msg_id
        self.keyword_suggested_response = [KeywordSuggestedResponse.from_dict(ksr) for ksr in keyword_suggested_response]
        self.extra = extra
