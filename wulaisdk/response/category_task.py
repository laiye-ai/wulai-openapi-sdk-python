"""
任务类
1. 查询场景列表
2. 创建场景
3. 更新场景
4. 删除场景
5. 查询意图列表
6. 创建意图
7. 更新意图
8. 删除意图
9. 查询触发器列表
10. 创建触发器
11. 更新触发器
12. 删除触发器
13. 查询词槽列表
14. 创建词槽
15. 更新词槽
16. 查询词槽
17. 删除词槽
18. 查询词槽数据来源
19. 创建词槽数据来源
20. 删除词槽数据来源
21. 查询消息发送单元
22. 创建消息发送单元
23. 更新消息发送单元
24. 查询询问填槽单元
25. 创建询问填槽单元
26. 更新询问填槽单元
27. 创建单元内回复
28.  更新单元内回复
29. 删除单元内回复
30. 查询意图终点单元
31. 创建意图终点单元
32. 更新意图终点单元
33. 查询单元列表
34. 创建单元关系
35. 删除单元关系
36. 删除单元
37. 查询任务待审核消息列表
38. 删除任务待审核消息
39. 更新意图状态
"""
from typing import List
from wulaisdk.response import BaseModel
from wulaisdk.response.msg_body import MsgBody


class Scene(BaseModel):
    """
    场景
    """
    description: str
    intent_switch_mode: str
    id: int
    smart_slot_filling_threshold: int
    name: str

    def __init__(self, description: str, intent_switch_mode: str, id: int,
                 smart_slot_filling_threshold: int, name: str) -> None:
        self.description = description
        self.intent_switch_mode = intent_switch_mode
        self.id = id
        self.smart_slot_filling_threshold = smart_slot_filling_threshold
        self.name = name


class Intent(BaseModel):
    """
    意图
    """
    scene_id: int
    status: bool
    lifespan_mins: int
    id: int
    name: str

    def __init__(self, scene_id: int, status: bool, lifespan_mins: int, id: int, name: str) -> None:
        self.scene_id = scene_id
        self.status = status
        self.lifespan_mins = lifespan_mins
        self.id = id
        self.name = name


class IntentTrigger(BaseModel):
    """
    触发器
    """
    text: str
    intent_id: int
    type: str
    id: int

    def __init__(self, text: str, intent_id: int, type: str, id: int) -> None:
        self.text = text
        self.intent_id = intent_id
        self.type = type
        self.id = id


class SlotSimple(BaseModel):
    """
    词槽(简版)
    """
    id: int
    name: str

    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name


class Slot(BaseModel):
    """
    词槽
    """
    scene_id: int
    query_slot_filling: bool
    id: int
    name: str

    def __init__(self, scene_id: int, query_slot_filling: bool, id: int, name: str) -> None:
        self.scene_id = scene_id
        self.query_slot_filling = query_slot_filling
        self.id = id
        self.name = name


class DataSource(BaseModel):
    """
    词槽数据来源
    """
    entity_id: int
    slot_id: int
    id: int

    def __init__(self, entity_id: int, slot_id: int, id: int) -> None:
        self.entity_id = entity_id
        self.slot_id = slot_id
        self.id = id


class RecommendIntent(BaseModel):
    """
    推荐意图
    """
    intent_id: int
    score: int
    intent_name: str

    def __init__(self, intent_id: int, score: int, intent_name: str) -> None:
        self.intent_id = intent_id
        self.score = score
        self.intent_name = intent_name


class QueryItem(BaseModel):
    """
    待审核问题
    """
    content: str
    id: int
    recommend_intent: RecommendIntent

    def __init__(self, content: str, id: int, recommend_intent: RecommendIntent) -> None:
        self.content = content
        self.id = id
        self.recommend_intent = RecommendIntent.from_dict(recommend_intent)


# api start
class Scenes(BaseModel):
    """
    查询场景列表
    """
    scenes: List[Scene]

    def __init__(self, scenes: List[Scene]) -> None:
        self.scenes = [Scene.from_dict(scene) for scene in scenes]


class CreateScene(BaseModel):
    """
    创建场景
    """
    scene: Scene

    def __init__(self, scene: Scene) -> None:
        self.scene = Scene.from_dict(scene)


class UpdateScene(BaseModel):
    """
    更新场景
    """
    scene: Scene

    def __init__(self, scene: Scene) -> None:
        self.scene = Scene.from_dict(scene)


class Intents(BaseModel):
    """
    查询意图列表
    """
    intents: List[Intent]

    def __init__(self, intents: List[Intent]) -> None:
        self.intents = [Intent.from_dict(intent) for intent in intents]


class CreateIntent(BaseModel):
    """
    创建意图
    """
    intent: Intent

    def __init__(self, intent: Intent) -> None:
        self.intent = Intent.from_dict(intent)


class UpdateIntent(BaseModel):
    """
    更新意图
    """
    intent: Intent

    def __init__(self, intent: Intent) -> None:
        self.intent = Intent.from_dict(intent)


class IntentTriggers(BaseModel):
    """
    触发器列表
    """
    intent_triggers: List[IntentTrigger]

    def __init__(self, intent_triggers: List[IntentTrigger]) -> None:
        self.intent_triggers = [IntentTrigger.from_dict(intent_trigger) for intent_trigger in intent_triggers]


class CreateIntentTrigger(BaseModel):
    """
    创建触发器
    """
    intent_trigger: IntentTrigger

    def __init__(self, intent_trigger: IntentTrigger) -> None:
        self.intent_trigger = IntentTrigger.from_dict(intent_trigger)


class UpdateIntentTrigger(BaseModel):
    """
    更新触发器
    """
    intent_trigger: IntentTrigger

    def __init__(self, intent_trigger: IntentTrigger) -> None:
        self.intent_trigger = IntentTrigger.from_dict(intent_trigger)


class Slots(BaseModel):
    """
    词槽列表
    """
    slots: List[SlotSimple]

    def __init__(self, slots: List[SlotSimple]) -> None:
        self.slots = [SlotSimple.from_dict(slot) for slot in slots]


class CreateSlot(BaseModel):
    """
    创建词槽
    """
    slot: Slot

    def __init__(self, slot: Slot) -> None:
        self.slot = Slot.from_dict(slot)


class UpdateSlot(BaseModel):
    """
    更新词槽
    """
    slot: Slot

    def __init__(self, slot: Slot) -> None:
        self.slot = Slot.from_dict(slot)


class GetSlot(BaseModel):
    """
    词槽详情
    """
    slot: Slot

    def __init__(self, slot: Slot) -> None:
        self.slot = Slot.from_dict(slot)


class SlotDataSource(BaseModel):
    """
    查询词槽数据来源
    """
    data_sources: List[DataSource]

    def __init__(self, data_sources: List[DataSource]) -> None:
        self.data_sources = [DataSource.from_dict(data_source) for data_source in data_sources]


class CreateSlotDataSource(BaseModel):
    """
    创建词槽数据来源
    """
    data_source: DataSource

    def __init__(self, data_source: DataSource) -> None:
        self.data_source = DataSource.from_dict(data_source)


class Response(BaseModel):
    """
    单元内回复
    """
    response: MsgBody
    id: int
    block_id: int

    def __init__(self, response: MsgBody, id: int, block_id: int) -> None:
        self.response = MsgBody.from_dict(response)
        self.id = id
        self.block_id = block_id


class Last(BaseModel):
    """
    意图终点跳转上个意图
    """

    def __init__(self, **kwargs) -> None:
        for k, v in kwargs.items():
            self.k = v


class End(BaseModel):
    """
    意图终点单元跳转指定意图
    """

    def __init__(self, **kwargs) -> None:
        for k, v in kwargs.items():
            self.k = v


class Specified(BaseModel):
    """
    意图终点单元跳转指定意图
    """
    id: int

    def __init__(self, id: int) -> None:
        self.id = id


class Action(BaseModel):
    """
    结束单元跳转方式 (指定意图 / 上个意图 / 不跳转)
    """

    def __init__(self, **kwargs) -> None:
        if "last" in kwargs:
            self.last = Last.from_dict(kwargs.get("last"))
        elif "end" in kwargs:
            self.end = End.from_dict(kwargs.get("end"))
        elif "specified" in kwargs:
            self.specified = Specified.from_dict(kwargs.get("specified"))
        else:
            for k, v in kwargs.items():
                setattr(self, k, v)


class EndBlock(BaseModel):
    """
    意图终点单元
    """
    action: Action
    slot_memorizing: bool
    intent_id: int
    id: int
    name: str

    def __init__(self, action: Action, slot_memorizing: bool, intent_id: int, id: int, name: str) -> None:
        self.action = Action.from_dict(action)
        self.slot_memorizing = slot_memorizing
        self.intent_id = intent_id
        self.id = id
        self.name = name


class Block(BaseModel):
    """
    单元
    """
    type: str
    id: int
    name: str

    def __init__(self, type: str, id: int, name: str) -> None:
        self.type = type
        self.id = id
        self.name = name


# 单元
class Default(BaseModel):
    """
    单元跳转条件 默认
    """

    def __init__(self, **kwargs) -> None:
        for k, v in kwargs.items():
            self.k = v


class InEntity(BaseModel):
    """
    单元跳转条件 属于(实体)
    """
    id: int

    def __init__(self, id: int) -> None:
        self.id = id


class NotInEntity(BaseModel):
    """
    单元跳转条件 不属于(实体)
    """
    id: int

    def __init__(self, id: int) -> None:
        self.id = id


class EqualTo(BaseModel):
    """
    单元跳转条件 等于
    """
    value: str

    def __init__(self, value: str) -> None:
        self.value = value


class NotEqualTo(BaseModel):
    """
    单元跳转条件 不等于
    """
    value: str

    def __init__(self, value: str) -> None:
        self.value = value


class LessThan(BaseModel):
    """
    单元跳转条件 小于
    """
    value: float

    def __init__(self, value: float) -> None:
        self.value = value


class LessThanOrEqualTo(BaseModel):
    """
    单元跳转条件 小于等于
    """
    value: float

    def __init__(self, value: float) -> None:
        self.value = value


class GreaterThan(BaseModel):
    """
    单元跳转条件 大于
    """
    value: float

    def __init__(self, value: float) -> None:
        self.value = value


class GreaterThanOrEqualTo(BaseModel):
    """
    单元跳转条件 大于等于
    """
    value: float

    def __init__(self, value: float) -> None:
        self.value = value


class MatchRegex(BaseModel):
    """
    单元跳转条件 符合正则
    """
    regex: str

    def __init__(self, regex: str) -> None:
        self.regex = regex


class DismatchRegex(BaseModel):
    """
    单元跳转条件 不符合正则
    """
    regex: str

    def __init__(self, regex: str) -> None:
        self.regex = regex


class Include(BaseModel):
    """
    单元跳转条件 包含
    """
    value: str

    def __init__(self, value: str) -> None:
        self.value = value


class Exclude(BaseModel):
    """
    单元跳转条件 不包含
    """
    value: str

    def __init__(self, value: str) -> None:
        self.value = value


class Condition(BaseModel):
    """
    单元跳转条件(默认 / 大于 / 大于等于 / 小于 / 小于等于 / 等于 / 不等于 / 包含 / 不包含 / 属于实体 / 不属于实体 / 符合正则 / 不符合正则)
    """

    def __init__(self, **kwargs) -> None:
        if "default" in kwargs:
            self.default = Default.from_dict(kwargs.get("default"))
        elif "in_entity" in kwargs:
            self.in_entity = InEntity.from_dict(kwargs.get("in_entity"))
        elif "not_in_entity" in kwargs:
            self.not_in_entity = NotInEntity.from_dict(kwargs.get("not_in_entity"))
        elif "equal_to" in kwargs:
            self.equal_to = EqualTo.from_dict(kwargs.get("equal_to"))
        elif "not_equal_to" in kwargs:
            self.not_equal_to = NotEqualTo.from_dict(kwargs.get("not_equal_to"))
        elif "greater_than" in kwargs:
            self.greater_than = GreaterThan.from_dict(kwargs.get("greater_than"))
        elif "greater_than_or_equal_to" in kwargs:
            self.greater_than_or_equal_to = GreaterThanOrEqualTo.from_dict(kwargs.get("greater_than_or_equal_to"))
        elif "less_than" in kwargs:
            self.less_than = LessThan.from_dict(kwargs.get("less_than"))
        elif "less_than_or_equal_to" in kwargs:
            self.less_than_or_equal_to = LessThanOrEqualTo.from_dict(kwargs.get("less_than_or_equal_to"))
        elif "match_regex" in kwargs:
            self.match_regex = MatchRegex.from_dict(kwargs.get("match_regex"))
        elif "match_regex" in kwargs:
            self.match_regex = MatchRegex.from_dict(kwargs.get("match_regex"))
        elif "dismatch_regex" in kwargs:
            self.dismatch_regex = DismatchRegex.from_dict(kwargs.get("dismatch_regex"))
        elif "include" in kwargs:
            self.include = Include.from_dict(kwargs.get("include"))
        elif "exclude" in kwargs:
            self.exclude = Exclude.from_dict(kwargs.get("exclude"))
        else:
            for k, v in kwargs.items():
                setattr(self, k, v)


class Connection(BaseModel):
    """
    单元关系
    """
    from_block_id: int
    to_block_id: int
    condition: Condition

    def __init__(self, from_block_id: int, to_block_id: int, condition: Condition) -> None:
        self.from_block_id = from_block_id
        self.to_block_id = to_block_id
        self.condition = Condition.from_dict(condition)


class Relation(BaseModel):
    """
    单元关系
    """
    connection: Connection
    intent_id: int
    id: int

    def __init__(self, connection: Connection, intent_id: int, id: int) -> None:
        self.connection = Connection.from_dict(connection)
        self.intent_id = intent_id
        self.id = id


class InformBlock(BaseModel):
    """
    消息发送单元
    """
    responses: List[MsgBody]
    connection: Connection
    mode: str
    intent_id: int
    id: int
    name: str

    def __init__(self, responses: List[MsgBody], connection: Connection, mode: str, intent_id: int, id: int, name: str) -> None:
        self.responses = [MsgBody.from_dict(response) for response in responses]
        self.connection = Connection.from_dict(connection)
        self.mode = mode
        self.intent_id = intent_id
        self.id = id
        self.name = name


class RequestBlock(BaseModel):
    """
    询问填槽单元
    """
    name: str
    default_slot_value: str
    slot_filling_when_asked: bool
    connections: List[Connection]
    slot_id: int
    mode: str
    request_count: int
    intent_id: int
    id: int
    responses: List[MsgBody]

    def __init__(
            self, name: str, default_slot_value: str, slot_filling_when_asked: bool,
            connections: List[Connection], slot_id: int, mode: str, request_count: int,
            intent_id: int, id: int, responses: List[MsgBody]) -> None:
        self.name = name
        self.default_slot_value = default_slot_value
        self.slot_filling_when_asked = slot_filling_when_asked
        self.connections = [Connection.from_dict(connection) for connection in connections]
        self.slot_id = slot_id
        self.mode = mode
        self.request_count = request_count
        self.intent_id = intent_id
        self.id = id
        self.responses = [MsgBody.from_dict(response) for response in responses]


class GetInformBlock(BaseModel):
    """
    查询消息发送单元
    """
    block: InformBlock

    def __init__(self, block: InformBlock) -> None:
        self.block = InformBlock.from_dict(block)


class CreateInformBlock(BaseModel):
    """
    创建消息发送单元
    """
    block: InformBlock

    def __init__(self, block: InformBlock) -> None:
        self.block = InformBlock.from_dict(block)


class UpdateInformBlock(BaseModel):
    """
    更新消息发送单元
    """
    block: InformBlock

    def __init__(self, block: InformBlock) -> None:
        self.block = InformBlock.from_dict(block)


class GetRequestBlock(BaseModel):
    """
    查询询问填槽单元
    """
    block: RequestBlock

    def __init__(self, block: RequestBlock) -> None:
        self.block = RequestBlock.from_dict(block)


class CreateRequestBlock(BaseModel):
    """
    创建询问填槽单元
    """
    block: RequestBlock

    def __init__(self, block: RequestBlock) -> None:
        self.block = RequestBlock.from_dict(block)


class UpdateRequestBlock(BaseModel):
    """
    更新询问填槽单元
    """
    block: RequestBlock

    def __init__(self, block: RequestBlock) -> None:
        self.block = RequestBlock.from_dict(block)


class CreateResponse(BaseModel):
    """
    创建单元内回复
    """
    response: Response

    def __init__(self, response: Response) -> None:
        self.response = Response.from_dict(response)


class UpdateResponse(BaseModel):
    """
    更新单元内回复
    """
    response: Response

    def __init__(self, response: Response) -> None:
        self.response = Response.from_dict(response)


class GetEndBlock(BaseModel):
    """
    查询意图终点单元
    """
    block: EndBlock

    def __init__(self, block: EndBlock) -> None:
        self.block = EndBlock.from_dict(block)


class CreateEndBlock(BaseModel):
    """
    创建意图终点单元
    """
    block: EndBlock

    def __init__(self, block: EndBlock) -> None:
        self.block = EndBlock.from_dict(block)


class UpdateEndBlock(BaseModel):
    """
    更新意图终点单元
    """
    block: EndBlock

    def __init__(self, block: EndBlock) -> None:
        self.block = EndBlock.from_dict(block)


class Blocks(BaseModel):
    """
    查询单元列表
    """
    blocks: List[Block]

    def __init__(self, blocks: List[Block]) -> None:
        self.blocks = [Block.from_dict(block) for block in blocks]


class CreateBlockRelation(BaseModel):
    """
    创建单元关系
    """
    relation: Relation

    def __init__(self, relation: Relation) -> None:
        self.relation = Relation.from_dict(relation)


class IntentTriggerLearning(BaseModel):
    """
    待审核问题列表
    """
    query_items: List[QueryItem]

    def __init__(self, query_items: List[QueryItem]) -> None:
        self.query_items = [QueryItem.from_dict(query_item) for query_item in query_items]


class UpdateIntentStatus(BaseModel):
    """
    更新意图状态
    """
    status: bool
    first_block_id: int
    intent_id: int
    update_time: str

    def __init__(self, status: bool, first_block_id: int, intent_id: int, update_time: str) -> None:
        self.status = status
        self.first_block_id = first_block_id
        self.intent_id = intent_id
        self.update_time = update_time
