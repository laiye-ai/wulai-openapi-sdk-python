from wulaisdk.client import WulaiClient
from wulaisdk.request import CommonRequest


pubkey = ""
secret = ""

client = WulaiClient(pubkey, secret)

action = "user/create"
params = {}
opts = {
    "method": "POST",
    "timeout": 3,
    "retry": 0,
    "other": {}
}
request = CommonRequest(action, params, opts)
resp = client.process_common_request(request)
