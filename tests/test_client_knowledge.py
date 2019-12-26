"""
知识点类api测试
"""
import os
import time
import pytest
import copy
import sys

from wulaisdk.client import WulaiClient


pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")
log_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_value_from_dict_array(li, search_key, value_key, reference):
    """
    在[{}, {}, ...]中找到合适的值
    :param li:
    :param search_key: 需要查询的key
    :param value_key: 目标值所在key
    :param reference: 对比值
    :return:
    """
    for di in li:
        if di[search_key] == reference:
            return di[value_key]
    return None


# knowledge test
def knowledge_c_timeupdate(k):
    new = copy.deepcopy(k)
    new["knowledge"]["standard_question"] += f"_{time.strftime('%Y-%m-%d/%H:%M:%S',time.localtime())}"
    return new


def knowledge_u_timeupdate(knowledge_c):
    new = copy.deepcopy(knowledge_c)
    knowledge_u = new["knowledge"]
    knowledge_u["standard_question"] += f"-改_{time.strftime('%Y-%m-%d/%H:%M:%S',time.localtime())}"
    return knowledge_u


knowledge_c_1 = {
    "knowledge": {
        "status": True,
        "standard_question": "sdk测试什么才是标准问",
        "respond_all": True,
        "maintained_by_user_attribute_group": True
    },
    "knowledge_tag_id": ""
}
knowledge_c_2 = {
    "knowledge": {
        "status": True,
        "standard_question": "sdk测试如何退换货",
        "respond_all": True,
        "maintained_by_user_attribute_group": True,
        "id": None
    },
    "knowledge_tag_id": ""
}


# normal
# knowledge_tags / knowledge_items / create_knowledge / update_knowledge / similar-questions
@pytest.mark.parametrize('page,page_size,knowledge_c,knowledge_u', [
    (1, 50, knowledge_c_timeupdate(knowledge_c_1), knowledge_u_timeupdate(knowledge_c_1)),
    (1, 50, knowledge_c_timeupdate(knowledge_c_2), knowledge_u_timeupdate(knowledge_c_2)),
])
def test_knowledge_tags(page, page_size, knowledge_c, knowledge_u):
    client = WulaiClient(pubkey, secret, debug=True)
    # tags
    #    -- without parent_k_tag_id
    resp_parent_tags = client.knowledge_tags(page, page_size)
    parent_k_tag_id = resp_parent_tags.knowledge_tags[0].id

    #    -- with parent_k_tag_id
    resp_second_tags = client.knowledge_tags(page, page_size, parent_k_tag_id)
    knowledge_tags = resp_second_tags.knowledge_tags
    knowledge_tags_di = [r.to_dict() for r in knowledge_tags]
    target_id = find_value_from_dict_array(knowledge_tags_di, "name", "id", "测试_yt")

    # create
    knowledge_c["knowledge_tag_id"] = target_id
    resp_knowledge_c = client.create_knowledge(knowledge_c)
    knowledge_id = resp_knowledge_c.knowledge_tag_knowledge.knowledge.id

    # update
    knowledge_u["id"] = knowledge_id
    resp_knowledge_u = client.update_knowledge(knowledge_u)

    # items
    resp = client.knowledge_items(page, page_size=10)

    assert resp_knowledge_u.knowledge.id == knowledge_id
    assert resp.page_count

    # similar-question
    # create
    similar_question_c = {
        "knowledge_id": knowledge_id,
        "question": "我能在你左边画条龙嘛？"
    }
    resp_similar_c = client.create_similar_question(similar_question_c)

    # update
    similar_question_id = resp_similar_c.similar_question.id
    similar_question_u = {
        "knowledge_id": knowledge_id,
        "question": "我能在你左边画条龙嘛？-改",
        "id": similar_question_id
    }
    resp_similar_u = client.update_similar_question(similar_question_u)

    # list
    resp_similar_list = client.similar_questions(page, page_size, knowledge_id, timeout=10)
    assert resp_similar_u.similar_question.to_dict() in [r.to_dict() for r in resp_similar_list.similar_questions]

    # delete
    resp = client.delete_similar_question(similar_question_id)
    assert isinstance(resp, dict)

    # delete knowledge
    resp = client.delete_knowledge(knowledge_id)
    assert isinstance(resp, dict)


# user-attribute test
# 区分3.6和3.7的测试内容
if sys.version_info.minor == 7:
    source_name = "微信"
else:
    source_name = "微博"
user_attribute_group_item_1 = {
    "user_attribute_user_attribute_value": [
        {
            "user_attribute": {"id": "101627"},
            "user_attribute_value": {"name": source_name}
        },
        {
            "user_attribute": {"id": "101629"},
            "user_attribute_value": {"name": "新用户"}
        }
    ],
    "user_attribute_group": {"name": f"{source_name}新用户"}
}
user_attribute_group_item_update_1 = {
    "user_attribute_user_attribute_value": [
        {
            "user_attribute": {"id": "101627"},
            "user_attribute_value": {"name": source_name}
        },
        {
            "user_attribute": {"id": "101629"},
            "user_attribute_value": {"name": "老用户"}
        }
    ],
    "user_attribute_group": {
        "id": "",
        "name": f"{source_name}老用户"
    }
}
user_attribute_group_answer_1 = {
    "answer": {
        "knowledge_id": "1048247",
        "msg_body": {"text": {"content": f"这是测试属性组的答案--{source_name}老用户"}},
    },
    "user_attribute_group_id": ""
}
user_attribute_group_answer_update_1 = {
    "answer": {
        "knowledge_id": "1048247",
        "msg_body": {"text": {"content": f"这是测试属性组的答案--{source_name}老用户"}},
        "id": ""
    },
    "user_attribute_group_id": ""
}


@pytest.mark.parametrize('user_attribute_group_item,user_attribute_group_item_update,user_attribute_group_answer,'
                         'user_attribute_group_answer_update,page,page_size', [
    (user_attribute_group_item_1, user_attribute_group_item_update_1, user_attribute_group_answer_1,
     user_attribute_group_answer_update_1, 1, 50),
])
def test_user_attribute(user_attribute_group_item, user_attribute_group_item_update, user_attribute_group_answer,
                        user_attribute_group_answer_update, page, page_size):
    # 属性组测试知识点分类id：125537，知识点id： 1048247
    client = WulaiClient(pubkey, secret, debug=True)
    # 创建属性组
    # todo：每一次测试后需要去项目里手动删除这个属性组
    resp_cuagi = client.create_user_attribute_group_items(user_attribute_group_item)
    # 更新属性组
    #   属性组id
    user_attribute_group_id = resp_cuagi.user_attribute_group_item.user_attribute_group.id

    user_attribute_group_item_update["user_attribute_group"]["id"] = user_attribute_group_id

    resp_uuagi = client.update_user_attribute_group_items(user_attribute_group_item_update)

    #   属性组名称
    user_attribute_group_name = resp_uuagi.user_attribute_group_item.user_attribute_group.name

    # 查询属性组及属性列表
    resp_uagi = client.user_attribute_group_items(page, page_size, timeout=10)
    user_attribute_group_ids = [uagi.user_attribute_group.id for uagi in resp_uagi.user_attribute_group_items]
    user_attribute_group_names = [uagi.user_attribute_group.name for uagi in resp_uagi.user_attribute_group_items]
    assert user_attribute_group_id in user_attribute_group_ids
    assert user_attribute_group_name in user_attribute_group_names

    # 创建属性组回复
    user_attribute_group_answer["user_attribute_group_id"] = user_attribute_group_id

    resp_cuaga = client.create_user_attribute_group_answer(user_attribute_group_answer)
    #   属性组答案id
    user_attribute_group_answer_id = resp_cuaga.user_attribute_group_answer.answer.id
    # 更新属性组回复
    user_attribute_group_answer_update["answer"]["id"] = user_attribute_group_answer_id
    user_attribute_group_answer_update["user_attribute_group_id"] = user_attribute_group_id

    resp_uuaga = client.update_user_attribute_group_answer(user_attribute_group_answer_update)
    assert resp_uuaga.user_attribute_group_answer.answer.id == user_attribute_group_answer_id
    # 查询属性组回复列表
    resp_answers = client.user_attribute_group_answers(page, page_size, timeout=10)
    resp_answers_2 = client.user_attribute_group_answers(page, page_size, {"knowledge_id": "1048247"}, timeout=10)
    assert isinstance(resp_answers.user_attribute_group_answers, list)
    assert isinstance(resp_answers_2.user_attribute_group_answers, list)

    # 删除属性组回复
    resp = client.delete_user_attribute_group_answer(user_attribute_group_answer_id)
