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
        client = WulaiClient(pubkey, secret, debug=debug, api_version="3")
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


