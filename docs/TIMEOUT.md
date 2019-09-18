### 超时重试处理方式

> 如果你想限制请求花费的时间，以及对失败的请求进行重试，可以自行配置


#### 使用
1. 使用封装好的api
```python
from wulaisdk.client import WulaiClient


pubkey = "your pubkey"
secret = "your secret"

client = WulaiClient(pubkey, secret)
user_id = "test_user"

opts = {
    "method": "POST",
    "retry": 2,
    "timeout": 3
}
resp = client.create_user(user_id, **opts)
```
2. 使用CommonRequest
```python
from wulaisdk.client import WulaiClient
from wulaisdk.request import CommonRequest


pubkey = "your pubkey"
secret = "your secret"

action = "/user/create"
params = {
    "avatar_url": "",
    "user_id": "test_user",
    "nickname": "测试用户"
}
opts = {
    "method": "POST",
    "retry": 2,
    "timeout": 3
}
client = WulaiClient(pubkey, secret, debug=False)
request = CommonRequest(action, params, opts)
resp = client.process_common_request(request)
```