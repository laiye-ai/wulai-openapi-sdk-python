### 使用CommonRequest进行api调用
> 当您要调用的某个产品的API没有提供SDK时，可以采用泛用型的API调用方式（CommonRequest）。  
使用CommonRequest调用方式可实现任意Open API接口的调用。

```python
import os

from wulaisdk.client import WulaiClient
from wulaisdk.request import CommonRequest


pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")

client = WulaiClient(pubkey, secret, api_version="v2")

# 自定义请求地址
action = "/user/create"
# 自定义请求参数
params = {
    "user_id": "tet_user",
    "avatar_url": "",
    "nickname": "testUser"
}
# 自定义请求方法、超时时间、重试次数
opts = {
    "method": "POST",
    "timeout": 3,
    "retry": 0
}
request = CommonRequest(action, params, opts)
resp = client.process_common_request(request)
```