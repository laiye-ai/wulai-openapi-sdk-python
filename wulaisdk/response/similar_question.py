"""
相似问
"""
from typing import List

from wulaisdk.response import BaseModel


class SimilarQuestion(BaseModel):
    knowledge_id: str
    question: str
    id: str

    def __init__(self, knowledge_id: str, question: str, id: str) -> None:
        self.knowledge_id = knowledge_id
        self.question = question
        self.id = id


class SimilarQuestionCreate(BaseModel):
    similar_question: SimilarQuestion

    def __init__(self, similar_question: SimilarQuestion) -> None:
        self.similar_question = SimilarQuestion.from_dict(similar_question)


class SimilarQuestionUpdate(BaseModel):
    similar_question: SimilarQuestion

    def __init__(self, similar_question: SimilarQuestion) -> None:
        self.similar_question = SimilarQuestion.from_dict(similar_question)


class SimilarQuestions(BaseModel):
    similar_questions: List[SimilarQuestion]
    page_count: int

    def __init__(self, similar_questions: List[SimilarQuestion], page_count: int) -> None:
        self.similar_questions = [SimilarQuestion.from_dict(sq) for sq in similar_questions]
        self.page_count = page_count
