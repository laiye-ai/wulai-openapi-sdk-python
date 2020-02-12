"""
知识点类
1. 创建知识点
2. 更新知识点
3. 删除知识点
4. 查询知识点列表
5. 查询知识点分类列表
6. 创建相似问
7. 更新相似问
8. 删除相似问
9. 查询相似问列表
10. 创建属性组
11. 更新属性组
12.查询属性组及属性列表
13. 创建属性组回复
14. 更新属性组回复
15. 查询属性组回复列表
16. 删除属性组回复
"""
from typing import List

from wulaisdk.response import BaseModel
from wulaisdk.response.msg_body import MsgBody
from wulaisdk.response.category_user import UserAttributeValue


class Knowledge(BaseModel):
    """
    知识点详情
    """
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
    """
    知识点
    """
    knowledge: Knowledge
    knowledge_tag_id: str

    def __init__(self, knowledge: Knowledge, knowledge_tag_id: str) -> None:
        self.knowledge = Knowledge.from_dict(knowledge)
        self.knowledge_tag_id = knowledge_tag_id


class KnowledgeCreate(BaseModel):
    """
    创建知识点
    """
    knowledge_tag_knowledge: KnowledgeTagKnowledge

    def __init__(self, knowledge_tag_knowledge: KnowledgeTagKnowledge) -> None:
        self.knowledge_tag_knowledge = KnowledgeTagKnowledge.from_dict(knowledge_tag_knowledge)


class KnowledgeUpdate(BaseModel):
    """
    更新知识点
    """
    knowledge: Knowledge

    def __init__(self, knowledge: Knowledge) -> None:
        self.knowledge = Knowledge.from_dict(knowledge)


class KnowledgeTag(BaseModel):
    """
    知识点分类
    """
    parent_knowledge_tag_id: str
    id: str
    name: str

    def __init__(self, parent_knowledge_tag_id: str, id: str, name: str) -> None:
        self.parent_knowledge_tag_id = parent_knowledge_tag_id
        self.id = id
        self.name = name


class SimilarQuestion(BaseModel):
    """
    相似问详情
    """
    knowledge_id: str
    question: str
    id: str

    def __init__(self, knowledge_id: str, question: str, id: str) -> None:
        self.knowledge_id = knowledge_id
        self.question = question
        self.id = id


class KnowledgeItem(BaseModel):
    """
    知识点
    """
    knowledge_tag: KnowledgeTag
    similar_questions: List[SimilarQuestion]
    knowledge: Knowledge

    def __init__(self, knowledge_tag: KnowledgeTag, similar_questions: List[SimilarQuestion], knowledge: Knowledge) -> None:
        self.knowledge_tag = KnowledgeTag.from_dict(knowledge_tag)
        self.similar_questions = [SimilarQuestion.from_dict(sq) for sq in similar_questions]
        self.knowledge = Knowledge.from_dict(knowledge)


class KnowledgeItems(BaseModel):
    """
    查询知识点列表
    """
    page_count: int
    knowledge_items: List[KnowledgeItem]

    def __init__(self, page_count: int, knowledge_items: List[KnowledgeItem]) -> None:
        self.page_count = page_count
        self.knowledge_items = [KnowledgeItem.from_dict(ki) for ki in knowledge_items]


class KnowledgeTags(BaseModel):
    """
    查询知识点分类列表
    """
    knowledge_tags: List[KnowledgeTag]
    page_count: int

    def __init__(self, knowledge_tags: List[KnowledgeTag], page_count: int) -> None:
        self.knowledge_tags = [KnowledgeTag.from_dict(kt) for kt in knowledge_tags]
        self.page_count = page_count


class KnowledgeTagCreate(BaseModel):
    """
    创建知识点分类
    """
    knowledge_tag: KnowledgeTag

    def __init__(self, knowledge_tag: KnowledgeTag) -> None:
        self.knowledge_tag = KnowledgeTag.from_dict(knowledge_tag)


class KnowledgeTagUpdate(BaseModel):
    """
    更新知识点分类
    """
    knowledge_tag: KnowledgeTag

    def __init__(self, knowledge_tag: KnowledgeTag) -> None:
        self.knowledge_tag = KnowledgeTag.from_dict(knowledge_tag)


# 相似问
class SimilarQuestionCreate(BaseModel):
    """
    创建相似问
    """
    similar_question: SimilarQuestion

    def __init__(self, similar_question: SimilarQuestion) -> None:
        self.similar_question = SimilarQuestion.from_dict(similar_question)


class SimilarQuestionUpdate(BaseModel):
    """
    更新相似问
    """
    similar_question: SimilarQuestion

    def __init__(self, similar_question: SimilarQuestion) -> None:
        self.similar_question = SimilarQuestion.from_dict(similar_question)


class SimilarQuestions(BaseModel):
    """
    查询相似问列表
    """
    similar_questions: List[SimilarQuestion]
    page_count: int

    def __init__(self, similar_questions: List[SimilarQuestion], page_count: int) -> None:
        self.similar_questions = [SimilarQuestion.from_dict(sq) for sq in similar_questions]
        self.page_count = page_count


# 属性组
class UserAttribute(BaseModel):
    """
    用户属性
    """
    value_type: str
    use_in_user_attribute_group: bool
    type: str
    id: str
    name: str

    def __init__(self, value_type: str, use_in_user_attribute_group: bool, type: str, id: str, name: str) -> None:
        self.value_type = value_type
        self.use_in_user_attribute_group = use_in_user_attribute_group
        self.type = type
        self.id = id
        self.name = name


class UserAttributeGroup(BaseModel):
    """
    用户属性组详情
    """
    id: str
    name: str

    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name


class UserAttributeUserAttributeValue(BaseModel):
    """
    属性
    """
    user_attribute: UserAttribute
    user_attribute_value: UserAttributeValue

    def __init__(self, user_attribute: UserAttribute, user_attribute_value: UserAttributeValue) -> None:
        self.user_attribute = UserAttribute.from_dict(user_attribute)
        self.user_attribute_value = UserAttributeValue.from_dict(user_attribute_value)


class UserAttributeGroupItem(BaseModel):
    """
    用户属性组及属性
    """
    user_attribute_user_attribute_values: List[UserAttributeUserAttributeValue]
    user_attribute_group: UserAttributeGroup

    def __init__(self, user_attribute_user_attribute_values: List[UserAttributeUserAttributeValue],
                 user_attribute_group: UserAttribute) -> None:
        self.user_attribute_user_attribute_values = [
            UserAttributeUserAttributeValue.from_dict(uauav) for uauav in user_attribute_user_attribute_values
        ]
        self.user_attribute_group = UserAttributeGroup.from_dict(user_attribute_group)


class CreateUserAttributeGroup(BaseModel):
    """
    创建属性组
    """
    user_attribute_group_item: UserAttributeGroupItem

    def __init__(self, user_attribute_group_item: UserAttributeGroupItem) -> None:
        self.user_attribute_group_item = UserAttributeGroupItem.from_dict(user_attribute_group_item)


class UpdateUserAttributeGroup(BaseModel):
    """
    更新属性组
    """
    user_attribute_group_item: UserAttributeGroupItem

    def __init__(self, user_attribute_group_item: UserAttributeGroupItem) -> None:
        self.user_attribute_group_item = UserAttributeGroupItem.from_dict(user_attribute_group_item)


class UpdateUserAttributeGroupItems(BaseModel):
    """
    查询属性组及属性列表
    """
    page_count: int
    user_attribute_group_items: List[UserAttributeGroupItem]

    def __init__(self, page_count: int, user_attribute_group_items: List[UserAttributeGroupItem]) -> None:
        self.page_count = page_count
        self.user_attribute_group_items = [
            UserAttributeGroupItem.from_dict(uagi) for uagi in user_attribute_group_items
        ]


class Answer(BaseModel):
    """
    回复
    """
    knowledge_id: str
    msg_body: MsgBody
    id: str

    def __init__(self, knowledge_id: str, msg_body: MsgBody, id: str) -> None:
        self.knowledge_id = knowledge_id
        self.msg_body = MsgBody.from_dict(msg_body)
        self.id = id


class UserAttributeGroupAnswer(BaseModel):
    """
    属性组回复
    """
    answer: Answer
    user_attribute_group_id: str

    def __init__(self, answer: Answer, user_attribute_group_id: str) -> None:
        self.answer = Answer.from_dict(answer)
        self.user_attribute_group_id = user_attribute_group_id


class CreateUserAttributeGroupAnswer(BaseModel):
    """
    创建属性组回复
    """
    user_attribute_group_answer: UserAttributeGroupAnswer

    def __init__(self, user_attribute_group_answer: UserAttributeGroupAnswer) -> None:
        self.user_attribute_group_answer = UserAttributeGroupAnswer.from_dict(user_attribute_group_answer)


class UpdateUserAttributeGroupAnswer(BaseModel):
    """
    更新属性组回复
    """
    user_attribute_group_answer: UserAttributeGroupAnswer

    def __init__(self, user_attribute_group_answer: UserAttributeGroupAnswer) -> None:
        self.user_attribute_group_answer = UserAttributeGroupAnswer.from_dict(user_attribute_group_answer)


class UserAttributeGroupAnswers(BaseModel):
    """
    查询属性组回复列表
    """
    user_attribute_group_answers: List[UserAttributeGroupAnswer]
    page_count: int

    def __init__(self, user_attribute_group_answers: List[UserAttributeGroupAnswer], page_count: int) -> None:
        self.user_attribute_group_answers = [
            UserAttributeGroupAnswer.from_dict(uaga) for uaga in user_attribute_group_answers
        ]
        self.page_count = page_count


class KnowledgeRelatedItem(BaseModel):
    """
    知识点（包含属性组信息）
    """
    knowledge_tag: KnowledgeTag
    similar_questions: List[SimilarQuestion]
    user_attribute_group_answers: List[UserAttributeGroupAnswer]
    knowledge: Knowledge

    def __init__(self, knowledge_tag: KnowledgeTag, similar_questions: List[SimilarQuestion],
                 user_attribute_group_answers: List[UserAttributeGroupAnswer], knowledge: Knowledge) -> None:
        self.knowledge_tag = KnowledgeTag.from_dict(knowledge_tag)
        self.similar_questions = [SimilarQuestion.from_dict(similar_question) for similar_question in similar_questions]
        self.user_attribute_group_answers = [
            UserAttributeGroupAnswer.from_dict(uaga) for uaga in user_attribute_group_answers
        ]
        self.knowledge = Knowledge.from_dict(knowledge)


class KnowledgeBatchCreate(BaseModel):
    """
    批量添加知识点列表
    """
    knowledge_related_items: List[KnowledgeRelatedItem]

    def __init__(self, knowledge_related_items: List[KnowledgeRelatedItem]) -> None:
        self.knowledge_related_items = [KnowledgeRelatedItem.from_dict(kri) for kri in knowledge_related_items]
