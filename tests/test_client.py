import os
import pytest

from wulaisdk.client import WulaiClient
from wulaisdk.request import CommonRequest

pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")


@pytest.mark.parametrize('debug,action,params,expected', [
    (False, 'userCreate',
     {
         "avatar_url": "",
         "user_id": "shierlou",
         "nickname": "测试用户-shierlou"
     },
     {}),
    (True, 'userCreate',
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
        "other": {}
    }
    client = WulaiClient(pubkey, secret, debug=debug)
    request = CommonRequest(action, params, opts)
    resp = client.process_common_request(request)
    assert resp == expected
