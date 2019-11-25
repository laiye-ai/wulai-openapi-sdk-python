"""
词库管理类
"""

from typing import List
from wulaisdk.response import BaseModel


class Entity(BaseModel):
    """
    实体
    """
    type: str
    id: int
    name: str

    def __init__(self, type: str, id: int, name: str) -> None:
        self.type = type
        self.id = id
        self.name = name


class DictionaryEntities(BaseModel):
    """
    全部实体概要列表
    """
    entities: List[Entity]

    def __init__(self, entities: List[Entity]) -> None:
        self.entities = [Entity.from_dict(entity) for entity in entities]


class Term(BaseModel):
    """
    专有词汇详情
    """
    id: int
    name: str

    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name


class TermItem(BaseModel):
    """
    专有词汇
    """
    term: Term
    synonyms: List[str]

    def __init__(self, term: Term, synonyms: List[str]) -> None:
        self.term = Term.from_dict(term)
        self.synonyms = synonyms


class DictionaryTerms(BaseModel):
    """
    专有词汇列表
    """
    term_item: List[TermItem]
    page_count: int

    def __init__(self, term_item: List[TermItem], page_count: int) -> None:
        self.term_item = [TermItem.from_dict(ti) for ti in term_item]
        self.page_count = page_count


class DictionaryTerm(BaseModel):
    """
    创建/更新专有词汇
    """
    term_item: TermItem

    def __init__(self, term_item: TermItem) -> None:
        self.term_item = TermItem.from_dict(term_item)


class Value(BaseModel):
    """
    实体值
    """
    synonyms: List[str]
    standard_value: str

    def __init__(self, synonyms: List[str], standard_value: str) -> None:
        self.synonyms = synonyms
        self.standard_value = standard_value


class IntentEntityValue(Value):
    """
    意图实体值
    """
    pass


class SystemEntityValue(BaseModel):
    """
    预设实体
    """
    description: str

    def __init__(self, description: str) -> None:
        self.description = description


class RegexEntityValue(BaseModel):
    """
    正则实体
    """
    regex: str

    def __init__(self, regex: str) -> None:
        self.regex = regex


class EnumEntityValue(BaseModel):
    """
    枚举实体值
    """
    values: List[Value]

    def __init__(self, values: List[Value]) -> None:
        self.values = [Value.from_dict(value) for value in values]


class EntityValue(BaseModel):
    """
    实体值
    """
    value: dict

    def __init__(self, **kwargs) -> None:
        if "intent_entity_value" in kwargs:
            self.text = IntentEntityValue.from_dict(kwargs.get("intent_entity_value"))
        elif "system_entity_value" in kwargs:
            self.image = SystemEntityValue.from_dict(kwargs.get("system_entity_value"))
        elif "regex_entity_value" in kwargs:
            self.custom = RegexEntityValue.from_dict(kwargs.get("regex_entity_value"))
        elif "enumeration_entity_value" in kwargs:
            self.video = EnumEntityValue.from_dict(kwargs.get("enumeration_entity_value"))
        else:
            for k, v in kwargs.items():
                setattr(self, k, v)


class EntityDetail(BaseModel):
    """
    实体详情
    """
    type: str
    id: int
    value: EntityValue
    name: str

    def __init__(self, type: str, id: int, value: Value, name: str) -> None:
        self.type = type
        self.id = id
        self.value = EntityValue.from_dict(value)
        self.name = name


class DictionaryEntity(BaseModel):
    """
    查询一个实体详情
    """
    entity: EntityDetail

    def __init__(self, entity: EntityDetail) -> None:
        self.entity = EntityDetail.from_dict(entity)


class EnumEntity(BaseModel):
    """
    枚举实体详情
    """
    values: List[Value]
    id: int
    name: str

    def __init__(self, values: List[Value], id: int, name: str) -> None:
        self.values = [Value.from_dict(value) for value in values]
        self.id = id
        self.name = name


class CreateEnumEntity(BaseModel):
    """
    创建枚举实体
    """
    enum_entity: EnumEntity

    def __init__(self, enum_entity: EnumEntity) -> None:
        self.enum_entity = EnumEntity.from_dict(enum_entity)


class CreateEnumEntityValue(BaseModel):
    """
    创建枚举实体值
    """
    enum_entity: EnumEntity

    def __init__(self, enum_entity: EnumEntity) -> None:
        self.enum_entity = EnumEntity.from_dict(enum_entity)


class IntentEntity(BaseModel):
    """
    意图实体
    """
    id: int
    value: Value
    name: str

    def __init__(self, id: int, value: Value, name: str) -> None:
        self.id = id
        self.value = Value.from_dict(value)
        self.name = name


class CreateIntentEntity(BaseModel):
    """
    创建意图实体
    """
    intent_entity: IntentEntity

    def __init__(self, intent_entity: IntentEntity) -> None:
        self.intent_entity = IntentEntity.from_dict(intent_entity)


class CreateIntentEntityValue(BaseModel):
    """
    创建意图实体值相似说法
    """
    intent_entity: IntentEntity

    def __init__(self, intent_entity: IntentEntity) -> None:
        self.intent_entity = IntentEntity.from_dict(intent_entity)
