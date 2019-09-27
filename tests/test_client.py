import os
import time
import pytest
import logging

from wulaisdk.client import WulaiClient
from wulaisdk.request import CommonRequest
from wulaisdk.exceptions import ClientException
from wulaisdk.response.bot_response import BotResponse
from wulaisdk.response.msg_body import MsgBody


pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")
log_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
    client = WulaiClient("111", secret, debug=debug)
    with pytest.raises(ClientException) as excinfo:
        client.create_user(user_id, avatar_url, nickname)
        assert excinfo.error_code == "SDK_INVALID_CREDENTIAL"


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
    ("shierlou", {"text": {"content": "测试message_sync"}}, str(int(time.time()*1000)))
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
#                   reset task bot
#############################################################
@pytest.mark.parametrize('user_id,msg_body,extra', [
    ("shierlou", {"text": {"content": "/restart"}}, "this is extra string")
])
def test_reset_task(user_id, msg_body, extra):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.get_bot_response(user_id, msg_body, extra)
    assert isinstance(resp.suggested_response[0].response[0].msg_body.text.content, str)
