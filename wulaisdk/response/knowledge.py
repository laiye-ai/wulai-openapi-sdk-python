"""
知识点
"""
from typing import List

from wulaisdk.response import BaseModel


class Knowledge(BaseModel):
    status: bool
    update_time: str
    maintained_by_user_attribute_group: bool
    standard_question: str
    create_time: str
    respond_all: bool
    id: str

    def __init__(self, status: bool, update_time: str, maintained_by_user_attribute_group: bool,
                 standard_question: str, create_time: str, respond_all: bool, id: str) -> None:
        self.status = status
        self.update_time = update_time
        self.maintained_by_user_attribute_group = maintained_by_user_attribute_group
        self.standard_question = standard_question
        self.create_time = create_time
        self.respond_all = respond_all
        self.id = id


class KnowledgeTagKnowledge(BaseModel):
    knowledge: Knowledge
    knowledge_tag_id: str

    def __init__(self, knowledge: Knowledge, knowledge_tag_id: str) -> None:
        self.knowledge = Knowledge.from_dict(knowledge)
        self.knowledge_tag_id = knowledge_tag_id


# 创建知识点
class KnowledgeCreate(BaseModel):
    knowledge_tag_knowledge: KnowledgeTagKnowledge

    def __init__(self, knowledge_tag_knowledge: KnowledgeTagKnowledge) -> None:
        self.knowledge_tag_knowledge = KnowledgeTagKnowledge.from_dict(knowledge_tag_knowledge)


# 更新知识点
class KnowledgeUpdate(BaseModel):
    knowledge: Knowledge

    def __init__(self, knowledge: Knowledge) -> None:
        self.knowledge = Knowledge.from_dict(knowledge)


class KnowledgeTag(BaseModel):
    parent_knowledge_tag_id: str
    id: str
    name: str

    def __init__(self, parent_knowledge_tag_id: str, id: str, name: str) -> None:
        self.parent_knowledge_tag_id = parent_knowledge_tag_id
        self.id = id
        self.name = name


class SimilarQuestion(BaseModel):
    knowledge_id: str
    question: str
    id: str

    def __init__(self, knowledge_id: str, question: str, id: str) -> None:
        self.knowledge_id = knowledge_id
        self.question = question
        self.id = id


class KnowledgeItem(BaseModel):
    knowledge_tag: KnowledgeTag
    similar_questions: List[SimilarQuestion]
    knowledge: Knowledge

    def __init__(self, knowledge_tag: KnowledgeTag, similar_questions: List[SimilarQuestion], knowledge: Knowledge) -> None:
        self.knowledge_tag = KnowledgeTag.from_dict(knowledge_tag)
        self.similar_questions = [SimilarQuestion.from_dict(sq) for sq in similar_questions]
        self.knowledge = Knowledge.from_dict(knowledge)


# 查询知识点列表
class KnowledgeItems(BaseModel):
    page_count: int
    knowledge_items: List[KnowledgeItem]

    def __init__(self, page_count: int, knowledge_items: List[KnowledgeItem]) -> None:
        self.page_count = page_count
        self.knowledge_items = [KnowledgeItem.from_dict(ki) for ki in knowledge_items]


# 查询知识点分类列表
class KnowledgeTags(BaseModel):
    knowledge_tags: List[KnowledgeTag]
    page_count: int

    def __init__(self, knowledge_tags: List[KnowledgeTag], page_count: int) -> None:
        self.knowledge_tags = [KnowledgeTag.from_dict(kt) for kt in knowledge_tags]
        self.page_count = page_count
