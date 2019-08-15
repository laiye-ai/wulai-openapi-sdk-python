import os

from wulaisdk.client import WulaiClient
from wulaisdk.request import CommonRequest


pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")

client = WulaiClient(pubkey, secret, debug=False)

action = "userCreate"
params = {}
opts = {
    "method": "POST",
    "headers": {},
    "timeout": 3,
    "retry": 0,
    "other": {}
}
request = CommonRequest(action, params, opts)
resp = client.process_common_request(request)
