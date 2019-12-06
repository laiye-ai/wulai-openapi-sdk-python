"""
任务类api测试
"""
import os
import sys
import time
import pytest

from wulaisdk.client import WulaiClient


pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")
log_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# 区分3.6和3.7的测试内容
if sys.version_info.minor == 7:
    tag = "v3.7"
else:
    tag = "v3.6"


#############################################################
#                           任务类
#############################################################
# 场景
@pytest.mark.parametrize('scene_create, scene_update', [
    # 标准场景创建
    ({
        "intent_switch_mode": "INTENT_SWITCH_MODE_STAY",
        "name": "测试场景-优先填槽",
        "smart_slot_filling_threshold": 0.7,
        "description": "测试场景-优先填槽"
     }, {
        "intent_switch_mode": "INTENT_SWITCH_MODE_STAY",
        "name": "测试场景-优先填槽-update",
        "smart_slot_filling_threshold": 0.69,
        "description": "测试场景-优先填槽-update",
        "id": ""
     }),
    # 不传智能填槽阈值
    ({
        "intent_switch_mode": "INTENT_SWITCH_MODE_SWITCH",
        "name": "测试场景-优先跳转",
        "description": "测试场景-优先跳转"
     }, {
        "intent_switch_mode": "INTENT_SWITCH_MODE_SWITCH",
        "name": "测试场景-优先跳转-update",
        "smart_slot_filling_threshold": 0.69,
        "description": "测试场景-优先跳转-update",
        "id": ""
     }),
    # 修改时不修改智能填槽阈值
    ({
        "intent_switch_mode": "INTENT_SWITCH_MODE_STAY",
        "name": "测试场景-优先填槽2",
        "smart_slot_filling_threshold": 0.69,
        "description": "测试场景-优先填槽"
     }, {
        "intent_switch_mode": "INTENT_SWITCH_MODE_STAY",
        "name": "测试场景-优先填槽2-update",
        "id": ""
     }),
])
def test_scenes(scene_create, scene_update):
    client = WulaiClient(pubkey, secret, debug=True)

    # 创建场景
    resp_create = client.create_scene(scene_create)
    scene_id = resp_create.scene.id

    # 更新场景
    scene_update["id"] = scene_id
    resp_update = client.update_scene(scene_update)

    assert scene_id == resp_update.scene.id

    # 查询场景列表
    resp_list = client.scenes()
    scene_ids = [scene.id for scene in resp_list.scenes]

    assert scene_id in scene_ids

    # 删除场景
    client.delete_scene(scene_id)

    # 查询场景列表
    resp_list = client.scenes()
    scene_ids = [scene.id for scene in resp_list.scenes]
    assert scene_id not in scene_ids


# 测试场景id： 12379
test_scene_id = 12379
# 测试意图id： 52034
test_intent_id = 52034
# 测试词槽id:
test_slot_id = 79396


# 意图
@pytest.mark.parametrize('intent_create, intent_update', [
    # 标准意图创建
    ({
        "scene_id": test_scene_id,
        "name": "测试意图",
        "lifespan_mins": 5
     }, {
        "id": "",
        "name": "测试意图-update",
        "lifespan_mins": 4
     }),
    # 标准意图创建-不传意图保留时间
    ({
        "scene_id": test_scene_id,
        "name": "测试意图2",
     }, {
        "id": "",
        "name": "测试意图2-update",
        "lifespan_mins": 4
     })
])
def test_intents(intent_create, intent_update):
    client = WulaiClient(pubkey, secret, debug=True)

    # 创建意图
    resp_create = client.create_intent(intent_create)
    intent_id = resp_create.intent.id

    # 更新意图
    intent_update["id"] = intent_id
    resp_update = client.update_intent(intent_update)

    assert intent_id == resp_update.intent.id

    # 查询意图列表
    resp_list = client.intents(intent_create["scene_id"])
    intent_ids = [intent.id for intent in resp_list.intents]

    assert intent_id in intent_ids

    # 删除意图
    client.delete_intent(intent_id)

    # 查询意图列表
    resp_list = client.intents(test_scene_id)
    intent_ids = [intent.id for intent in resp_list.intents]

    assert intent_id not in intent_ids


# 触发器
@pytest.mark.parametrize('intent_trigger_create, intent_trigger_update', [
    # 关键词匹配触发器创建
    ({
        "text": "关键词匹配触发文本",
        "intent_id": test_intent_id,
        "type": "TRIGGER_TYPE_EXACT_MATCH_KEYWORD"
     }, {
        "id": "",
        "text": "关键词触发文本更新"
     }),
    # 关键词包含触发器创建
    ({
        "text": "关键词包含触发文本",
        "intent_id": test_intent_id,
        "type": "TRIGGER_TYPE_INCLUDE_KEYWORD"
     }, {
        "id": "",
        "text": "关键词包含触发文本更新"
     }),
    # 相似说法触发器创建
    ({
        "text": "相似说法触发文本",
        "intent_id": test_intent_id,
        "type": "TRIGGER_TYPE_SENTENCE"
     }, {
        "id": "",
        "text": "相似说法触发文本更新"
     }),
])
def test_intent_trigger(intent_trigger_create, intent_trigger_update):
    client = WulaiClient(pubkey, secret, debug=True)

    # 创建触发器
    resp_create = client.create_intent_trigger(intent_trigger_create)
    intent_trigger_id = resp_create.intent_trigger.id

    # 更新触发器
    intent_trigger_update["id"] = intent_trigger_id
    resp_update = client.update_intent_trigger(intent_trigger_update)

    assert intent_trigger_id == resp_update.intent_trigger.id

    # 查询触发器列表
    resp_list = client.intent_triggers(intent_trigger_create["intent_id"], 1, 50)
    intent_trigger_ids = [intent_trigger.id for intent_trigger in resp_list.intent_triggers]

    assert intent_trigger_id in intent_trigger_ids

    # 删除触发器
    client.delete_intent_trigger(intent_trigger_id)

    # 查询触发器列表
    resp_list = client.intent_triggers(intent_trigger_create["intent_id"], 1, 50)
    intent_trigger_ids = [intent_trigger.id for intent_trigger in resp_list.intent_triggers]

    assert intent_trigger_id not in intent_trigger_ids


# 词槽
# 创建词槽背后应该是异步的，收到response时不代表词槽已经创建。
@pytest.mark.parametrize('slot_create, slot_update, data_source', [
    # 词槽
    ({
        "scene_id": test_scene_id,
        "name": f"词槽1-{tag}",
        "query_slot_filling": False
     }, {
        "id": "",
        "name": f"词槽1-{tag}",
        "query_slot_filling": True
     }, {
        "entity_id": 2,  # 星座
        "slot_id": ""
    }),
    # 词槽更新-不传name
    ({
        "scene_id": test_scene_id,
        "name": f"词槽2-3.{sys.version_info.minor}",
     }, {
        "id": "",
        "query_slot_filling": True
     }, {
        "entity_id": 2,  # 星座
        "slot_id": ""
    })
])
def test_slot(slot_create, slot_update, data_source):
    client = WulaiClient(pubkey, secret, debug=False)

    # 创建词槽
    resp_create = client.create_slot(slot_create)
    slot_id = resp_create.slot.id

    # 创建词槽数据来源
    data_source["slot_id"] = slot_id
    resp_data_source_create = client.create_slot_data_source(data_source)
    data_source_id = resp_data_source_create.data_source.id
    assert resp_data_source_create.data_source.entity_id == 2
    assert data_source_id

    # 查询词槽数据来源
    resp_data_source = client.slot_data_source(slot_id)
    slot_ids_ds = [one_data_source.slot_id for one_data_source in resp_data_source.data_sources]
    assert slot_id in slot_ids_ds

    # 删除词槽数据来源
    client.delete_slot_data_source(data_source_id)

    # 更新词槽
    slot_update["id"] = slot_id
    time.sleep(1)
    resp_update = client.update_slot(slot_update)

    assert slot_id == resp_update.slot.id

    # 查询词槽
    slot = client.get_slot(slot_id)
    assert slot.slot.name

    # 查询词槽列表
    resp_list = client.slots(slot_create["scene_id"], 1, 50)
    slot_ids = [slot.id for slot in resp_list.slots]

    assert slot_id in slot_ids

    # 删除词槽
    client.delete_slot(slot_id)

    # 查询词槽列表
    resp_list = client.slots(slot_create["scene_id"], 1, 50)
    slot_ids = [slot.id for slot in resp_list.slots]

    assert slot_id not in slot_ids


# 单元
# 消息发送单元
@pytest.mark.parametrize('inform_block_create, inform_block_update, response_create, response_update', [
    # 常规
    ({
        "intent_id": test_intent_id,
        "name": "消息发送单元1",
        "mode": "RESPONSE_ALL"
     }, {
        "id": "",
        "name": "消息发送单元1-update",
        "mode": "RESPONSE_ALL"
     }, {
        "block_id": "",
        "response": {
            "text": {
                "content": "这是消息发送单元"
            }
        }
    }, {
        "id": "",
        "response": {
            "image": {
                "resource_url": "https://www.baidu.com/img/bd_logo1.png"
            }
        }
    }),
    ({
        "intent_id": test_intent_id,
        "name": "消息发送单元2",
        "mode": "RESPONSE_LOOP"
     }, {
        "id": "",
        "name": "消息发送单元2-update",
        "mode": "RESPONSE_RANDOM"
     }, {
        "block_id": "",
        "response": {
            # "rich_text": {
            #     "resource_url": "https://www.baidu.com/img/bd_logo1.png"
            # }
            "custom": {
                "content": "测试custom自定义消息"
            }
        }
    }, {
        "id": "",
        "response": {
            "text": {
                "content": "https://www.baidu.com/img/bd_logo1.png"
            }
        }
    }),
])
def test_inform_block(inform_block_create, inform_block_update, response_create, response_update):
    client = WulaiClient(pubkey, secret, debug=True)

    # 创建消息发送单元
    resp_create = client.create_inform_block(inform_block_create)
    inform_block_id = resp_create.block.id

    # 更新消息发送单元
    inform_block_update["id"] = inform_block_id
    resp_update = client.update_inform_block(inform_block_update)

    assert inform_block_id == resp_update.block.id

    # 查询消息发送单元
    resp = client.inform_block(inform_block_id)

    assert resp.block.name

    # 创建单元内回复
    response_create["block_id"] = inform_block_id
    resp_resp_create = client.create_block_response(response_create)
    assert resp_resp_create.response.response.to_dict()
    key = list(resp_resp_create.response.response.__dict__.keys())[0]
    assert getattr(resp_resp_create.response.response, key).to_dict()

    resp_id = resp_resp_create.response.id

    # 更新单元内回复
    response_update["id"] = resp_id
    resp_resp_update = client.update_block_response(response_update)
    assert resp_resp_update.response.response.to_dict()
    key = list(resp_resp_update.response.response.__dict__.keys())[0]
    assert getattr(resp_resp_update.response.response, key).to_dict()

    # 删除单元内回复
    client.delete_block_response(resp_id)

    # 删除单元
    client.delete_block(inform_block_id)


# 询问填槽单元
@pytest.mark.parametrize('request_block_create, request_block_update, response_create', [
    # 常规
    ({
        "intent_id": test_intent_id,
        "name": "询问填槽单元1",
        "mode": "RESPONSE_ALL",
        "default_slot_value": "_default",
        "slot_filling_when_asked": False,
        "request_count": 2,
        "slot_id": test_slot_id
     }, {
        "id": "",
        "name": "询问填槽单元1-update",
        "slot_filling_when_asked": True,
     }, {
        "block_id": "",
        "response": {
            "text": {
                "content": "这是询问填槽单元"
            }
        }
    }),
])
def test_request_block(request_block_create, request_block_update, response_create):
    client = WulaiClient(pubkey, secret, debug=True)

    # 创建询问填槽单元
    resp_create = client.create_request_block(request_block_create)
    block_id = resp_create.block.id

    # 更新询问填槽单元
    request_block_update["id"] = block_id
    resp_update = client.update_request_block(request_block_update)

    assert block_id == resp_update.block.id

    # 查询询问填槽单元
    resp = client.request_block(block_id)

    assert resp.block.name

    # 创建单元内回复
    response_create["block_id"] = block_id
    resp_resp_create = client.create_block_response(response_create)
    assert resp_resp_create.response.response.to_dict()
    key = list(resp_resp_create.response.response.__dict__.keys())[0]
    assert getattr(resp_resp_create.response.response, key).to_dict()

    resp_id = resp_resp_create.response.id

    # 删除单元内回复
    client.delete_block_response(resp_id)

    # 删除单元
    client.delete_block(block_id)


# 意图终点单元
@pytest.mark.smoke
@pytest.mark.parametrize('end_block_create, end_block_update_1, end_block_update_2', [
    # 常规
    ({
        "intent_id": "",
        "name": "终点单元1",
        "slot_memorizing": False,
        "action": {"last": {}}
     }, {
        "id": "",
        "name": "终点单元1-update",
        "slot_memorizing": True,
        "action": {"end": {}}
     }, {
        "id": "",
        "name": "终点单元1-update",
        "slot_memorizing": True,
        "action": {"specified": {"id": test_intent_id}}
    }),
])
def test_end_block(end_block_create, end_block_update_1, end_block_update_2):
    client = WulaiClient(pubkey, secret, debug=True)

    # 创建意图
    intent = {
        "scene_id": test_scene_id,
        "name": "测试意图3",
        "lifespan_mins": 5
    }
    resp_create_intent = client.create_intent(intent)
    intent_id = resp_create_intent.intent.id

    end_block_create["intent_id"] = intent_id

    # 创建意图终点单元
    resp_create = client.create_end_block(end_block_create)
    block_id = resp_create.block.id

    # 更新意图终点单元
    end_block_update_1["id"] = block_id
    end_block_update_2["id"] = block_id
    resp_update_1 = client.update_end_block(end_block_update_1)
    resp_update_2 = client.update_end_block(end_block_update_2)

    assert block_id == resp_update_1.block.id
    assert block_id == resp_update_2.block.id

    # 查询询问填槽单元
    resp = client.end_block(block_id)

    assert resp.block.name

    # 删除单元
    client.delete_block(block_id)

    # 删除意图
    client.delete_intent(intent_id)


# 待审核消息
def test_intent_trigger_learning():
    client = WulaiClient(pubkey, secret, debug=True)

    # 查询任务待审核消息列表
    resp_list = client.intent_trigger_learning(1, 50)
    assert resp_list.to_dict()
    query_item = resp_list.query_items[0]
    assert query_item.recommend_intent.intent_name
    intent_trigger_learning_id = query_item.id

    # 删除任务待审核消息
    client.delete_intent_trigger_learning(intent_trigger_learning_id)


# 完整意图测试: 单元列表、单元关系、更新意图状态
def test_whole():
    client = WulaiClient(pubkey, secret, debug=True)

    # 创建意图
    intent = {
        "scene_id": test_scene_id,
        "name": "全流程测试意图",
        "lifespan_mins": 5
    }
    resp_create_intent = client.create_intent(intent)
    intent_id = resp_create_intent.intent.id

    # 创建消息发送单元
    inform_block_1 = {
        "intent_id": intent_id,
        "name": "消息发送1",
        "mode": "RESPONSE_ALL"
    }
    inform_block_2 = {
        "intent_id": intent_id,
        "name": "消息发送2",
        "mode": "RESPONSE_ALL"
    }
    resp_inform_block_id1 = client.create_inform_block(inform_block_1)
    resp_inform_block_id2 = client.create_inform_block(inform_block_2)
    inform_block_1_id = resp_inform_block_id1.block.id
    inform_block_2_id = resp_inform_block_id2.block.id

    # 创建单元内回复
    response_1_1 = {
        "block_id": inform_block_1_id,
        "response": {
            "text": {
                "content": "回复1_1"
            }
        }
    }
    response_1_2 = {
        "block_id": inform_block_1_id,
        "response": {
            "text": {
                "content": "回复1_2"
            }
        }
    }
    response_2_1 = {
        "block_id": inform_block_2_id,
        "response": {
            "text": {
                "content": "回复2_1"
            }
        }
    }
    client.create_block_response(response_1_1)
    client.create_block_response(response_1_2)
    client.create_block_response(response_2_1)

    # 创建询问单元
    request_block = {
        "intent_id": intent_id,
        "name": "询问单元1",
        "mode": "RESPONSE_ALL",
        "default_slot_value": "_default",
        "slot_filling_when_asked": False,
        "request_count": 2,
        "slot_id": test_slot_id
     }
    resp_request_block = client.create_request_block(request_block)
    request_block_id = resp_request_block.block.id
    # 创建单元内回复
    response_1_1 = {
        "block_id": request_block_id,
        "response": {
            "text": {
                "content": "询问1:"
            }
        }
    }
    client.create_block_response(response_1_1)

    # 创建意图终点单元
    end_block = {
        "intent_id": intent_id,
        "name": "终点单元1",
        "slot_memorizing": False,
        "action": {"end": {}}
     }
    resp_end_block = client.create_end_block(end_block)
    end_block_id = resp_end_block.block.id

    # 创建单元关系
    # 1.消息单元1->询问单元
    relation_1 = {
        "connection": {
            "from_block_id": inform_block_1_id,
            "to_block_id": request_block_id
        },
        "intent_id": intent_id
    }
    resp_relation_1 = client.create_block_relation(relation_1)
    assert resp_relation_1.relation.id

    # 2. 询问单元->消息单元2
    relation_2 = {
        "connection": {
            "from_block_id": request_block_id,
            "to_block_id": inform_block_2_id,
            "condition": {"less_than_or_equal_to": {"value": 50}}
        },
        "intent_id": intent_id
    }
    resp_relation_2 = client.create_block_relation(relation_2)
    assert resp_relation_2.relation.intent_id

    # 3. 询问单元->意图终点单元
    relation_3 = {
        "connection": {
            "from_block_id": request_block_id,
            "to_block_id": end_block_id,
            "condition": {"greater_than": {"value": 50}}
        },
        "intent_id": intent_id
    }
    resp_relation_3 = client.create_block_relation(relation_3)
    assert resp_relation_3.relation.connection.condition.greater_than.value

    # 4. 询问单元->消息单元2
    relation_4 = {
        "connection": {
            "from_block_id": request_block_id,
            "to_block_id": inform_block_2_id,
            "condition": {"default": {}}
        },
        "intent_id": intent_id
    }
    resp_relation_4 = client.create_block_relation(relation_4)
    relation_4_id = resp_relation_4.relation.id
    # 5. 消息单元2->意图终点单元
    relation_5 = {
        "connection": {
            "from_block_id": inform_block_2_id,
            "to_block_id": end_block_id
        },
        "intent_id": intent_id
    }
    resp_relation_5 = client.create_block_relation(relation_5)
    assert resp_relation_5.relation.connection.from_block_id

    # 更新意图状态
    status = True
    first_block_id = inform_block_1_id

    client.update_intent_status(status, first_block_id, intent_id)

    # 删除单元关系
    client.delete_block_relation(relation_4_id)

    # 查询单元列表
    resp_list = client.blocks(intent_id, 1, 50)
    assert resp_list.blocks
    block_ids = [block.id for block in resp_list.blocks]
    assert inform_block_1_id in block_ids
    assert inform_block_2_id in block_ids
    assert request_block_id in block_ids
    assert end_block_id in block_ids

    # 删除意图
    client.delete_intent(intent_id)
