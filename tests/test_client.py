import os
import pytest

from wulaisdk.client import WulaiClient
from wulaisdk.request import CommonRequest, CreateUserRequest, GetBotResponseRequest
from wulaisdk.exceptions import ClientException, ServerException

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


@pytest.mark.parametrize('debug,params,expected', [
    (True,
     {
         "avatar_url": "",
         "user_id": "shierlou",
         "nickname": "测试用户-shierlou"
     }, {}),
    (False,
     {
         "user_id": "shierlou",
         "nickname": "测试用户-shierlou"
     }, {}),
    (True,
     {
         "avatar_url": "",
         "user_id": "shierlou",
     }, {}),
    (True,
     {
         "user_id": "shierlou",
     }, {}),
])
def test_create_user_normal(debug, params, expected):
    opts = {
        "method": "POST",
        "timeout": 3,
        "retry": 0,
    }
    client = WulaiClient(pubkey, secret, debug=debug)
    request = CreateUserRequest(params, opts)
    resp = client.process_common_request(request)
    assert resp == expected


@pytest.mark.parametrize('debug,params', [
    (True,
     {
         "avatar_url": "",
         "nickname": "测试用户-shierlou"
     }),
    (False,
     {
         "avatar_url": "",
         "user_id": "",
         "nickname": "测试用户-shierlou"
     }),
])
def test_create_user_error(debug, params):
    opts = {
        "method": "POST",
        "timeout": 3,
        "retry": 0,
    }
    client = WulaiClient(pubkey, secret, debug=debug)
    request = CreateUserRequest(params, opts)
    with pytest.raises(ClientException) as excinfo:
        client.process_common_request(request)
        assert excinfo.error_msg == "SDK_INVALID_PARAMS"
