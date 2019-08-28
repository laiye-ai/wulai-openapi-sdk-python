import os

from wulaisdk.client import WulaiClient
from wulaisdk.request import CommonRequest


pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")

client = WulaiClient(pubkey, secret, debug=False)

action = "/user/create"
params = {
    "user_id": "tet_user",
    "avatar_url": "",
    "nickname": "testUser"
}
opts = {
    "method": "POST",
    "timeout": 3,
    "retry": 0
}
request = CommonRequest(action, params, opts)
resp = client.process_common_request(request)
