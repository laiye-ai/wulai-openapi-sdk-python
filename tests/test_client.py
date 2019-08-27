import os
import pytest

from wulaisdk.client import WulaiClient
from wulaisdk.request import CommonRequest
from wulaisdk.exceptions import ClientException

pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")


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
def test_client(debug, action, params, expected):
    opts = {
        "method": "POST",
        "timeout": 3,
        "retry": 0,
    }
    client = WulaiClient(pubkey, secret, debug=debug)
    request = CommonRequest(action, params, opts)
    resp = client.process_common_request(request)
    assert resp == expected


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
        assert excinfo.error_msg == "SDK_INVALID_PARAMS"


# getBotResponse test
@pytest.mark.parametrize('user_id,msg_body,extra,expected', [
    ("shierlou", {"text": {"content": "你好"}}, "this is extra string",
     {"is_dispatch": "", "suggested_response": {}, "msg_id": ""})
])
def test_get_bot_response_normal(user_id, msg_body, extra, expected):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.get_bot_response(user_id, msg_body, extra)
    assert set(resp.keys()) == set(expected.keys())
