"""
自然语言处理类
1. 实体抽取
2. 分词&词性标注
3. 导入待聚类语料
4. 清空待聚类语料
5. 发起聚类
6. 获取聚类结果列表
7. 删除聚类结果
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


class MiningUpload(BaseModel):
    """
    导入待聚类语料
    """
    succeeded_count: int
    failed_count: int
    duplicated_count: int

    def __init__(self, succeeded_count: int, failed_count: int, duplicated_count: int) -> None:
        self.succeeded_count = succeeded_count
        self.failed_count = failed_count
        self.duplicated_count = duplicated_count


class MiningExecute(BaseModel):
    """
    发起聚类
    """
    status: str

    def __init__(self, status: str) -> None:
        self.status = status


class Sentence(BaseModel):
    """
    聚类簇中的句子
    """
    id: int
    sentence: str

    def __init__(self, id: int, sentence: str) -> None:
        self.id = id
        self.sentence = sentence


class Cluster(BaseModel):
    """
    聚类簇
    """
    id: int
    sentences: List[Sentence]

    def __init__(self, id: int, sentences: List[Sentence]) -> None:
        self.id = id
        self.sentences = [Sentence.from_dict(sentence) for sentence in sentences]


class MiningResult(BaseModel):
    """
    获取聚类结果列表
    """
    status: str
    clusters: List[Cluster]
    page_count: int

    def __init__(self, status: str, clusters: List[Cluster], page_count: int) -> None:
        self.status = status
        self.clusters = [Cluster.from_dict(cluster) for cluster in clusters]
        self.page_count = page_count
