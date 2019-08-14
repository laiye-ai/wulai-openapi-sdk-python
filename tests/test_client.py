import os
import pytest

from wulaisdk.client import WulaiClient
from wulaisdk.request import CommonRequest

pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")

client = WulaiClient(pubkey, secret)


@pytest.mark.parametrize('action,params,expected', [
    ('userCreate',
     {
         "avatar_url": "",
         "user_id": "shierlou",
         "nickname": "测试用户-shierlou"
     },
     {}),
    # ('2*10', 20),
    # ('1==1', False),
])
def test_eval(action, params, expected):
    opts = {
        "method": "POST",
        "timeout": 3,
        "retry": 0,
        "other": {}
    }
    request = CommonRequest(action, params, opts)
    resp = client.process_common_request(request)
    assert resp == expected
