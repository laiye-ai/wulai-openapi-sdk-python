import os
import time
import pytest
import logging
import copy
import sys

from wulaisdk.client import WulaiClient
from wulaisdk.request import CommonRequest
from wulaisdk.exceptions import ClientException
from wulaisdk.response.bot_response import BotResponse
from wulaisdk.response.msg_body import MsgBody

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


@pytest.mark.parametrize('debug,action,params,expected', [
    (False, '/user/create',
     {
         "avatar_url": "",
         "user_id": "shierlou",
         "nickname": "测试用户-shierlou"
     },
     {}),
    (True, '/user/create',
     {
         "avatar_url": "",
         "user_id": "shierlou",
         "nickname": "测试用户-shierlou"
     },
     {}),
])
def test_common_request(debug, action, params, expected):
    opts = {
        "method": "POST",
        "timeout": 3,
        "retry": 0,
    }
    client = WulaiClient(pubkey, secret, debug=debug)
    request = CommonRequest(action, params, opts)
    resp = client.process_common_request(request)
    assert resp == expected


# test invalid http method
@pytest.mark.parametrize('debug,action,params,opts', [
    (False, '/user/create',
     {
         "avatar_url": "",
         "user_id": "shierlou",
         "nickname": "测试用户-shierlou"
     },
     {
         "method": "PUT",
         "timeout": 3,
         "retry": 0,
     }),
    (True, '/user/create',
     {
         "avatar_url": "",
         "user_id": "shierlou",
         "nickname": "测试用户-shierlou"
     },
     {
         "method": "GET",
         "timeout": 3,
         "retry": 0,
     }),
])
def test_http_method(debug, action, params, opts):
    client = WulaiClient(pubkey, secret, debug=debug)
    with pytest.raises(ClientException) as excinfo:
        request = CommonRequest(action, params, opts)
        client.process_common_request(request)
        assert excinfo.error_msg == "SDK_METHOD_NOT_ALLOW"


# test api_version
@pytest.mark.parametrize('debug,user_id,avatar_url,nickname', [
    (True, "shierlou", "", "测试用户-shierlou"),
    (True, "shierlou", "", ""),
])
def test_api_version(debug, user_id, avatar_url, nickname):
    with pytest.raises(ClientException) as excinfo:
        client = WulaiClient(pubkey, secret, debug=debug, api_version="v3")
        client.create_user(user_id, avatar_url, nickname)
        assert excinfo.error_code == "SDK_INVALID_API_VERSION"


# test log FileHandler
@pytest.mark.parametrize('handler', [
    logging.FileHandler(log_dir_path + '/logs/wulaisdk.log')
])
def test_log_handler(handler):
    client = WulaiClient(pubkey, secret, debug=True)
    client.add_logger_handler(handler)
    client.create_user("shierlou")


# test invalid credential
@pytest.mark.parametrize('debug,user_id,avatar_url,nickname', [
    (True, "shierlou", "", "测试用户-shierlou"),
    (True, "shierlou", "", ""),
])
def test_credential(debug, user_id, avatar_url, nickname):
    client = WulaiClient("asEGUJtCyLkHvTmm8vE0bXLe5ebGs2PP00df19808441f2cfff", secret, debug=debug)
    with pytest.raises(ClientException) as excinfo:
        client.create_user(user_id, avatar_url, nickname)
        assert excinfo.error_code == "SDK_INVALID_CREDENTIAL"


#############################################################
#                          用户类
#############################################################
# createUser test
@pytest.mark.parametrize('debug,user_id,avatar_url,nickname,expected', [
    (True, "shierlou", "", "测试用户-shierlou", {}),
    (True, "shierlou", "", "", {}),
])
def test_create_user_normal_1(debug, user_id, avatar_url, nickname, expected):
    client = WulaiClient(pubkey, secret, debug=debug)
    resp = client.create_user(user_id, avatar_url, nickname)
    assert resp == expected


@pytest.mark.parametrize('debug,user_id,expected', [
    (True, "shierlou", {}),
    (True, "shierlou", {}),
])
def test_create_user_normal_2(debug, user_id, expected):
    client = WulaiClient(pubkey, secret, debug=debug)
    resp = client.create_user(user_id)
    assert resp == expected


@pytest.mark.parametrize('debug,user_id', [
    (True, ""),
    (False, 123),
])
def test_create_user_error(debug, user_id):
    client = WulaiClient(pubkey, secret, debug=debug)
    with pytest.raises(ClientException) as excinfo:
        client.create_user(user_id)
        assert excinfo.error_code == "SDK_INVALID_PARAMS"


# 获取用户属性列表
@pytest.mark.parametrize('filter, page, page_size', [
    (None, 1, 50),
    (None, 2, 30),
    ({"use_in_user_attribute_group": True}, 1, 30),
    ({"use_in_user_attribute_group": False}, 1, 30)
])
def test_user_attributes(filter, page, page_size):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.user_attributes(page, page_size, filter)
    assert resp


# 查询用户属性值
@pytest.mark.parametrize('user_id', [
    "shierlou"
])
def test_user_user_attribute(user_id):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.user_user_attribute(user_id)
    assert resp


# 给用户添加属性值
@pytest.mark.parametrize('user_attribute_user_attribute_value, user_id', [
    ([{"user_attribute": {"id": "101627"}, "user_attribute_value": {"name": "微博"}}], "shierlou"),
    ([{"user_attribute": {"id": "101629"}, "user_attribute_value": {"name": "老用户"}}], "shierlou"),
    ([
        {"user_attribute": {"id": "101627"}, "user_attribute_value": {"name": "微信"}},
        {"user_attribute": {"id": "101629"}, "user_attribute_value": {"name": "新用户"}}
    ], "shierlou"),
])
def test_create_user_attribute(user_attribute_user_attribute_value, user_id):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.create_user_attribute(user_attribute_user_attribute_value, user_id)
    assert 1


#############################################################
#                          对话类
#############################################################
# getBotResponse test
@pytest.mark.parametrize('user_id,msg_body,extra', [
    ("shierlou", {"text": {"content": "你好"}}, "this is extra string")
])
def test_get_bot_response_normal(user_id, msg_body, extra):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.get_bot_response(user_id, msg_body, extra)
    assert resp.suggested_response[0].response[0].msg_body.text.content == '你好，有什么可以为你服务的吗？(*╹▽╹*)'


# getBotResponse for image test
@pytest.mark.parametrize('user_id,msg_body', [
    ("shierlou", {"text": {"content": "图片如何回复"}})
])
def test_get_bot_response_image(user_id, msg_body):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.get_bot_response(user_id, msg_body)
    assert isinstance(resp.suggested_response[0].response[0].msg_body.image.resource_url, str)


# createUserUserAttribute test
@pytest.mark.parametrize('user_id,user_attribute_user_attribute_value,expected', [
    ("shierlou", [
        {"user_attribute": {"id": "101343"}, "user_attribute_value": {"name": "新用户"}},
        {"user_attribute": {"id": "101344"}, "user_attribute_value": {"name": "小区a"}},
    ], {}),
])
def test_create_user_user_attribute_normal(user_id, user_attribute_user_attribute_value, expected):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.create_user_user_attribute(user_id, user_attribute_user_attribute_value)
    assert resp == expected


# getKeyWordBotResponse test
@pytest.mark.parametrize('user_id,msg_body,expected', [
    ("shierlou", {"text": {"content": "关键词测试"}}, "哈哈哈，这是关键词😃")
])
def test_get_keyword_bot_response_normal(user_id, msg_body, expected):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.get_keyword_bot_response(user_id, msg_body)
    assert resp.to_dict()["keyword_suggested_response"][0]["response"][0]["msg_body"]["text"]["content"] == expected
    assert resp.keyword_suggested_response[0].response[0].msg_body.text.content == expected


# getQABotResponse test
@pytest.mark.parametrize('user_id,msg_body,extra,expected', [
    ("shierlou", {"text": {"content": "吃了吗"}}, "this is extra string", "服务你第一，吃饭第二，请问有什么可以帮助你的吗？")
])
def test_get_qa_bot_response_normal(user_id, msg_body, extra, expected):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.get_qa_bot_response(user_id, msg_body, extra)
    assert resp.to_dict()["qa_suggested_response"][0]["response"][0]["msg_body"]["text"]["content"] == expected
    assert resp.qa_suggested_response[0].response[0].msg_body.text.content == expected


# getQABotResponse for image test
@pytest.mark.parametrize('user_id,msg_body,extra', [
    ("shierlou", {"text": {"content": "图片如何回复"}}, "this is extra string")
])
def test_get_qa_bot_response_image(user_id, msg_body, extra):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.get_qa_bot_response(user_id, msg_body, extra)
    assert isinstance(resp.qa_suggested_response[0].response[0].msg_body.image.resource_url, str)


# getTaskBotResponse test
@pytest.mark.parametrize('user_id,msg_body,extra', [
    ("shierlou", {"text": {"content": "我想查尺码"}}, "this is extra string")
])
def test_get_task_bot_response_normal(user_id, msg_body, extra):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.get_task_bot_response(user_id, msg_body, extra)
    assert "text" in resp.to_dict()["task_suggested_response"][0]["response"][0]["msg_body"].keys()
    assert isinstance(resp.task_suggested_response[0].response[0].msg_body.text.content, str)


# syncMessage test
@pytest.mark.parametrize('user_id,msg_body,msg_ts', [
    ("shierlou", {"text": {"content": "测试message_sync"}}, str(int(time.time() * 1000)))
])
def test_sync_message(user_id, msg_body, msg_ts):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.sync_message(user_id, msg_body, msg_ts)
    assert "msg_id" in resp.to_dict()
    assert isinstance(resp.msg_id, str)


# receiveMessage test
@pytest.mark.parametrize('user_id,msg_body', [
    ("shierlou", {"text": {"content": "测试receive_message"}})
])
def test_receive_message(user_id, msg_body):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.receive_message(user_id, msg_body)
    assert "msg_id" in resp.to_dict()
    assert isinstance(resp.msg_id, str)


# getMessageHistory test
@pytest.mark.parametrize('user_id,num', [
    ("shierlou", 50)
])
def test_message_history(user_id, num):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.get_message_history(user_id, num)
    assert resp.to_dict()
    assert isinstance(resp.msg[0].user_info.nickname, str)
    assert isinstance(resp.msg[0].msg_body.to_dict(), dict)
    msg_body = resp.msg[0].msg_body
    if hasattr(msg_body, "text"):
        assert isinstance(msg_body.text.content, str)
    elif hasattr(msg_body, "image"):
        assert isinstance(msg_body.image.resource_url, str)


# bot-response wrapper test
@pytest.mark.parametrize('body', [
    {"msg_id": "123", "test": "test", "is_dispatch": False, "suggested_response": [], "extra": ""}
])
def test_err_response(body):
    assert BotResponse.from_dict(body)


# msg_body wrapper test
@pytest.mark.parametrize('body', [
    {"text": {"content": "hhhh"}},
    {"image": {"resource_url": "hhhh"}},
    {"test": {"test": "test"}},
])
def test_err_response(body):
    assert MsgBody.from_dict(body)


#############################################################
#                         知识点类
#############################################################
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
    resp_parent_tags = client.knowledge_tags(page, page_size)
    parent_k_tag_id = resp_parent_tags.knowledge_tags[0].id

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
    assert isinstance(resp_answers.user_attribute_group_answers, list)

    # 删除属性组回复
    # resp = client.delete_user_attribute_group_answer(user_attribute_group_answer_id)


#############################################################
#                   reset task bot
#############################################################
@pytest.mark.parametrize('user_id,msg_body,extra', [
    ("shierlou", {"text": {"content": "/restart"}}, "this is extra string")
])
def test_reset_task(user_id, msg_body, extra):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.get_bot_response(user_id, msg_body, extra)
    assert isinstance(resp.suggested_response[0].response[0].msg_body.text.content, str)
