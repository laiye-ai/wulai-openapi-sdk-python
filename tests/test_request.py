import os
import pytest

from wulaisdk.request import CommonRequest
from wulaisdk.exceptions import ClientException

pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")


@pytest.mark.parametrize('action,params,opts,expected', [
    ('/user/create',
     {
         "avatar_url": "",
         "user_id": "shierlou",
         "nickname": "测试用户-shierlou"
     },
     {
         "method": "POST",
         "timeout": 3,
         "retry": 0,
     }, CommonRequest),
    ('/user/create',
     {
         "avatar_url": "",
         "user_id": "shierlou",
         "nickname": "测试用户-shierlou"
     },
     {
         "method": "POST",
         "timeout": 3,
         "retry": 3,
     }, CommonRequest),
])
def test_common_request_normal(action, params, opts, expected):
    request = CommonRequest(action, params, opts)
    assert isinstance(request, expected)


@pytest.mark.parametrize('action,params,opts,mode', [
    ('/user/create',
     '{"avatar_url": "", "user_id": "shierlou", "nickname": "测试用户-shierlou"}',
     {
         "method": "GET",
         "timeout": 3,
         "retry": 0,
     }, 1),
    ('/user/create',
     {
         "avatar_url": "",
         "user_id": "shierlou",
         "nickname": "测试用户-shierlou"
     },
     '{"method": "POST", "timeout": 3, "retry": 3}', 1),
    ({"url": "user/create"},
     {
         "avatar_url": "",
         "user_id": "shierlou",
         "nickname": "测试用户-shierlou"
     },
     {
         "method": "GET",
         "timeout": 3,
         "retry": 0,
     }, 2),
])
def test_common_request_error(action, params, opts, mode):
    if mode == 1:
        with pytest.raises(ClientException) as excinfo:
            CommonRequest(action, params, opts)
            assert excinfo.error_msg == "SDK_INVALID_PARAMS"
    elif mode == 2:
        with pytest.raises(ClientException) as excinfo:
            CommonRequest(action, params, opts)
            assert excinfo.error_msg == "SDK_INVALID_ACTION"


@pytest.mark.parametrize('headers,excepted', [
    ({"a": 1}, {
        "a": 1
    }),
])
def test_set_headers(headers, excepted):
    action = '/user/create'
    params = {
     "avatar_url": "",
     "user_id": "shierlou",
     "nickname": "测试用户-shierlou"
    }
    opts = {
     "method": "POST",
     "timeout": 3,
     "retry": 0,
    }
    request = CommonRequest(action, params, opts)
    request.set_headers(headers)
    assert request.headers == excepted


@pytest.mark.parametrize('k,v,excepted', [
    ("a", 1, {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "a": 1
    }),
])
def test_add_headers(k,v, excepted):
    action = '/user/create'
    params = {
     "avatar_url": "",
     "user_id": "shierlou",
     "nickname": "测试用户-shierlou"
    }
    opts = {
     "method": "POST",
     "timeout": 3,
     "retry": 0,
    }
    request = CommonRequest(action, params, opts)
    request.add_headers(k, v)
    assert request.headers == excepted

