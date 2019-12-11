"""
属性组
"""
from typing import List

from wulaisdk.response import BaseModel
from wulaisdk.response.msg_body import MsgBody


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


class UserAttributeValue(BaseModel):
    """
    用户属性值
    """
    id: str
    name: str

    def __init__(self, id: str, name: str) -> None:
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


class UserAttributeTotal(BaseModel):
    """
    用户属性
    """
    name: str
    lifespan: int
    value_type: str
    use_in_user_attribute_group: bool
    type: str
    id: str

    def __init__(self, name: str, lifespan: int, value_type: str, use_in_user_attribute_group: bool, type: str,
                 id: str) -> None:
        self.name = name
        self.lifespan = lifespan
        self.value_type = value_type
        self.use_in_user_attribute_group = use_in_user_attribute_group
        self.type = type
        self.id = id


class UserAttributeTotalUserAttributeValue(BaseModel):
    """
    属性
    """
    user_attribute: UserAttributeTotal
    user_attribute_value: UserAttributeValue

    def __init__(self, user_attribute: UserAttributeTotal, user_attribute_value: UserAttributeValue) -> None:
        self.user_attribute = UserAttributeTotal.from_dict(user_attribute)
        self.user_attribute_value = UserAttributeValue.from_dict(user_attribute_value)


class UserAttributeTotalUserAttributeValues(BaseModel):
    """
    属性列表
    """
    user_attribute: UserAttributeTotal
    user_attribute_value: List[UserAttributeValue]

    def __init__(self, user_attribute: UserAttributeTotal, user_attribute_value: List[UserAttributeValue]) -> None:
        self.user_attribute = UserAttributeTotal.from_dict(user_attribute)
        self.user_attribute_value = [UserAttributeValue.from_dict(uav) for uav in user_attribute_value]


class UserUserAttribute(BaseModel):
    """
    用户属性值
    """
    user_attribute_user_attribute_values: List[UserAttributeTotalUserAttributeValue]

    def __init__(self, user_attribute_user_attribute_values: List[UserAttributeTotalUserAttributeValue]) -> None:
        self.user_attribute_user_attribute_values = [
            UserAttributeTotalUserAttributeValue.from_dict(uauav) for uauav in user_attribute_user_attribute_values
        ]


class UserAttributes(BaseModel):
    """
    用户属性列表
    """
    page_count: int
    user_attribute_user_attribute_values: List[UserAttributeTotalUserAttributeValues]

    def __init__(self, page_count: int,
                 user_attribute_user_attribute_values: List[UserAttributeTotalUserAttributeValues]) -> None:
        self.page_count = page_count
        self.user_attribute_user_attribute_values = [
            UserAttributeTotalUserAttributeValues.from_dict(uauav) for uauav in user_attribute_user_attribute_values
        ]


class GetUser(BaseModel):
    """
    查询用户信息
    """
    avatar_url: str
    nickname: str

    def __init__(self, avatar_url: str, nickname: str) -> None:
        self.avatar_url = avatar_url
        self.nickname = nickname
