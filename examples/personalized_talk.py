"""
个性化对话场景


在基础对话的基础上，对不同用户回复不同的内容。实现效果：发送消息给机器人，机器人根据用户的属性判断回复内容并作出回复。

对接前提：
1. 调用方提供接入机器人的渠道。
2. 已经在吾来机器人平台搭建并训练了机器人。
3. 已经在吾来机器人平台定义了用户属性。

对接步骤：
1. 调用 user/create 接口，传入 user_id，创建用户；
2. 调用 user/user-attribute/create 接口，传入 user_id 和该用户的用户属性；
3. 调用 msg/bot-response 接口，传入 user_id 和该用户发来的消息；
4. 机器人会返回1~10条可能的回复，按照置信度从高到低排序。
   调用方可根据自己业务需要，依据置信度参数 score 的高低或者 is_send 的值，选择一条或多条回复。
"""
import os

from wulaisdk.client import WulaiClient

pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")

client = WulaiClient(pubkey, secret, debug=False)

# 创建用户
resp_cu = client.create_user("test_user", nickname="测试用户")

# 添加属性值
user_attribute_user_attribute_value = [
    {"user_attribute": {"id": "101343"}, "user_attribute_value": {"name": "新用户"}},
    {"user_attribute": {"id": "101344"}, "user_attribute_value": {"name": "小区a"}},
]
resp_crra = client.create_user_user_attribute("test_user", user_attribute_user_attribute_value)

# 获取回复
msg_body = {
    "text": {"content": "你好"}
}
resp_gbr = client.get_bot_response("test_user", msg_body)
