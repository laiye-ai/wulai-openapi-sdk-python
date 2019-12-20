"""
用户类
1. 创建用户
2. 查询用户信息 √
3. 更新用户信息
4. 获取用户属性列表 √
5. 查询用户的属性值 √
6. 给用户添加属性值
"""
from typing import List

from wulaisdk.response import BaseModel


class UserAttributeValue(BaseModel):
    """
    用户属性值
    """
    id: str
    name: str

    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name


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
