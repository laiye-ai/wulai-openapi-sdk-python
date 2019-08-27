import os
import pytest

from wulaisdk.request import CommonRequest, CreateUserRequest, GetBotResponseRequest
from wulaisdk.exceptions import ClientException, ServerException

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
def test_common_normal(action, params, opts, expected):
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
def test_common_error(action, params, opts, mode):
    if mode == 1:
        with pytest.raises(ClientException) as excinfo:
            CommonRequest(action, params, opts)
            assert excinfo.error_msg == "SDK_INVALID_PARAMS"
    elif mode == 2:
        with pytest.raises(ClientException) as excinfo:
            CommonRequest(action, params, opts)
            assert excinfo.error_msg == "SDK_NOT_SUPPORT"


