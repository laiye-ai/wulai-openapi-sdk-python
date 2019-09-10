# wulai-openapi-sdk-python
[![Build Status](https://travis-ci.org/laiye-ai/wulai-openapi-sdk-python.svg?branch=master)](https://travis-ci.org/laiye-ai/wulai-openapi-sdk-python)
[![codecov](https://codecov.io/gh/laiye-ai/wulai-openapi-sdk-python/branch/master/graph/badge.svg)](https://codecov.io/gh/laiye-ai/wulai-openapi-sdk-python)
[![PyPi version](https://pypip.in/v/wulaisdk/badge.png)](https://crate.io/packages/$REPO/)


#### 快速开始
欢迎使用吾来开发者工具套件（SDK）。


#### 使用条件
> python >= 3.4


#### 安装
`pip install wulaisdk`


#### 如何使用
```
# 基础对话场景
from wulaisdk.client import WulaiClient

# 创建client示例
pubkey = "your pubkey"
secret = "your secret"
client = WulaiClient(pubkey, secret)

# 创建用户
user_id = "test_user"
avatar_url = ""
nick_name = "testUser"
resp = client.create_user(user_id, avatar_url, nick_name)

# 获取回复
msg_body = {
    "text": {
        "content": "你好"
    }
}
extra = ""
resp = client.get_bot_response(user_id, msg_body, extra)
```

#### 场景示例
详见examples
```
基础对话场景 - base_talk.py
个性化对话场景 - personalized_talk.py

如封装后的api调用不满足需求
可参考origin.py自定义请求
```


#### 常用接口
```
client = WulaiClient(pubkey, secret)

# 创建用户
client.create_user()
# 获取机器人回复
client.get_bot_response()
# 添加用户属性值
client.create_user_user_attribute()

```