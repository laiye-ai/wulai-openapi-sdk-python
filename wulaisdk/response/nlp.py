"""
自然语言处理类
"""
from wulaisdk.response import BaseModel
from typing import List


class EnumerationEntity(BaseModel):
    """
    枚举实体
    """
    text: str
    synonyms: List[str]
    standard_value: str
    name: str

    def __init__(self, text: str, synonyms: List[str], standard_value: str, name: str) -> None:
        self.text = text
        self.synonyms = synonyms
        self.standard_value = standard_value
        self.name = name


class RegexEntity(BaseModel):
    """
    正则实体
    """
    text: str
    name: str

    def __init__(self, text: str, name: str) -> None:
        self.text = text
        self.name = name


class SystemEntity(BaseModel):
    """
    系统实体
    """
    text: str
    standard_value: str
    name: str

    def __init__(self, text: str, standard_value: str, name: str) -> None:
        self.text = text
        self.standard_value = standard_value
        self.name = name


class Entity(BaseModel):
    entity: dict

    def __init__(self, **kwargs) -> None:
        if "enumeration_entity" in kwargs:
            self.enumeration_entity = EnumerationEntity.from_dict(kwargs.get("enumeration_entity"))
        elif "regex_entity" in kwargs:
            self.regex_entity = RegexEntity.from_dict(kwargs.get("regex_entity"))
        elif "system_entity" in kwargs:
            self.system_entity = SystemEntity.from_dict(kwargs.get("system_entity"))
        else:
            for k, v in kwargs.items():
                setattr(self, k, v)


class EntityElement(BaseModel):
    """
    实体抽取的返回值
    """
    type: str
    idx_start: int
    entity: Entity

    def __init__(self, type: str, idx_start: int, entity: Entity) -> None:
        self.type = type
        self.idx_start = idx_start
        self.entity = Entity.from_dict(entity)


class EntityExtract(BaseModel):
    """
    实体抽取
    """
    entities: List[EntityElement]

    def __init__(self, entities: List[EntityElement]) -> None:
        self.entities = [EntityElement.from_dict(entity) for entity in entities]


class Token(BaseModel):
    """
    文本&词性
    """
    text: str
    pos: str
    idx_start: int

    def __init__(self, text: str, pos: str, idx_start: int) -> None:
        self.text = text
        self.pos = pos
        self.idx_start = idx_start


class Tokenize(BaseModel):
    """
    分词&词性标注
    """
    tokens: List[Token]

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = [Token.from_dict(token) for token in tokens]
