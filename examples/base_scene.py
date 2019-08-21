import os

from wulaisdk.client import WulaiClient
from wulaisdk.request import CreateUserRequest, GetBotResponseRequest


pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")

client = WulaiClient(pubkey, secret, debug=False)

action = "userCreate"
params_cu = {
    "user_id": "test",
    "avatar_url": "",
    "nickname": "测试用户"
}
opts = {
    "method": "POST",
    "timeout": 3,
    "retry": 0
}
request_cu = CreateUserRequest(params_cu, opts)
# request_cu.update_headers({"a": "1"})
resp_cu = client.process_common_request(request_cu)

params_gbr = {
    "user_id": "test",
    "msg_body": {"text": {"content": "你好"}},
    "extra": ""
}
request_gbr = GetBotResponseRequest(params_gbr, opts)
resp_gbr = client.process_common_request(request_gbr)
