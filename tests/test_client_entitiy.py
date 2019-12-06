import os
import sys
import pytest

from wulaisdk.client import WulaiClient
from wulaisdk.exceptions import ClientException


pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")
log_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# 区分3.6和3.7的测试内容
if sys.version_info.minor == 7:
    tag = "v3.7"
else:
    tag = "v3.6"


#############################################################
#                          词库管理类
#############################################################
# 查看全部实体概要
@pytest.mark.parametrize('page, page_size', [
    (1, 50),
    (3, 50),
    (5, 50)
])
def test_dictionary_entities(page, page_size):
    client = WulaiClient(pubkey, secret, debug=True)

    resp = client.dictionary_entities(page, page_size)
    if not resp.entities:
        assert resp.to_dict()
        assert not resp.entities
    else:
        entity = resp.entities[-1]

        entity_id = entity.id

        resp_entity = client.dictionary_entity(entity_id)
    
        assert resp.to_dict()
        assert resp_entity.to_dict()


# 专有词汇
@pytest.mark.parametrize('term_item_create,term_item_update,page,page_size', [
    ({
        "term": {"name": f"yt_专有名词_1_{tag}"},
        "synonyms": [f"yt_专有名词_1", f"yt_名词_1", f"专有名词_1"]
    }, {
        "term": {"id": "", "name": f"yt_专有名词_1_update"},
        "synonyms": [f"yt_专有名词_1"]
    }, 1, 50),
])
def test_dictionary_term(term_item_create, term_item_update, page, page_size):
    client = WulaiClient(pubkey, secret, debug=True)

    # 创建专有词汇
    resp_create = client.create_dictionary_term(term_item_create)
    term_id = resp_create.term_item.term.id
    assert term_id

    # 更新专有词汇
    term_item_update["term"]["id"] = term_id
    resp_update = client.update_dictionary_term(term_item_update)
    term_id_2 = resp_update.term_item.term.id
    assert term_id == term_id_2

    # 专有词汇列表
    resp_list = client.dictionary_terms(page, page_size)
    term_ids = [term_item.term.id for term_item in resp_list.term_item]

    assert term_id in term_ids

    # 删除专有词汇
    client.delete_dictionary_term(term_id)


# 枚举实体
@pytest.mark.parametrize('enum_entity, entity_value, entity_value_part, entity_value_total', [
    ({"name": f"枚举实体测试1_{tag}"},
     {"synonyms": ["标准值1", "标准1", "准值1"], "standard_value": "标准值1"},
     {"synonyms": ["准值1"], "standard_value": "标准值1"},
     {"standard_value": "标准值1"},
     ),
])
def test_dictionary_entities_enum(enum_entity, entity_value, entity_value_part, entity_value_total):
    client = WulaiClient(pubkey, secret, debug=True)

    # 创建枚举实体
    resp_entity_enum = client.create_dictionary_entity_enumeration(enum_entity)
    entity_enum_id = resp_entity_enum.enum_entity.id

    # 创建枚举实体值
    resp_create = client.create_dictionary_entity_enumeration_value(entity_enum_id, entity_value)

    assert resp_create.enum_entity.id

    # 删除枚举实体部分值
    client.delete_dictionary_entity_enumeration_value(entity_enum_id, entity_value_part)

    # 删除枚举实体标准值
    client.delete_dictionary_entity_enumeration_value(entity_enum_id, entity_value_total)

    resp_entity = client.dictionary_entity(entity_enum_id)

    assert resp_entity.entity.name == enum_entity["name"]

    # 删除枚举实体
    client.delete_dictionary_entity(entity_enum_id)

    with pytest.raises(ClientException) as excinfo:
        client.dictionary_entity(entity_enum_id)
        assert excinfo.error_code == "SDK_INVALID_PARAMS"


# 意图实体
@pytest.mark.parametrize('intent_entity, entity_value_update, entity_value_delete', [
    ({"standard_value": "发烧", "name": f"意图实体测试1_{tag}"},
     ["体温有点高", "额头发热", "发烧"],
     ["额头发热"],
     ),
])
def test_dictionary_entities_intent(intent_entity, entity_value_update, entity_value_delete):
    client = WulaiClient(pubkey, secret, debug=True)

    # 创建意图实体
    resp_entity_intent = client.create_dictionary_entity_intent(intent_entity)
    entity_intent_id = resp_entity_intent.intent_entity.id

    # 创建意图实体值相似说法
    resp_create = client.create_dictionary_entity_intent_value(entity_intent_id, entity_value_update)

    assert entity_intent_id == resp_create.intent_entity.id

    # 删除意图实体值相似说法
    client.delete_dictionary_entity_intent_value(entity_intent_id, entity_value_delete)

    # 删除实体
    client.delete_dictionary_entity(entity_intent_id)

    with pytest.raises(ClientException) as excinfo:
        client.dictionary_entity(entity_intent_id)
        assert excinfo.error_code == "SDK_INVALID_PARAMS"

