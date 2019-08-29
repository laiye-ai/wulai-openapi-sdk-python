import os
import pytest
import logging

from wulaisdk.client import WulaiClient
from wulaisdk.request import CommonRequest
from wulaisdk.exceptions import ClientException

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
         "method": "DELETE",
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
@pytest.mark.parametrize('user_id,msg_body,extra,expected', [
    ("shierlou", {"text": {"content": "你好"}}, "this is extra string",
     {"is_dispatch": "", "suggested_response": {}, "msg_id": ""})
])
def test_get_bot_response_normal(user_id, msg_body, extra, expected):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.get_bot_response(user_id, msg_body, extra)
    assert set(resp.keys()) == set(expected.keys())


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
