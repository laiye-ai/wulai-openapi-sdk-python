"""
异步基础对话场景


通过异步方式实现用户与机器人的交互，比基础对话稍微复杂。实现效果：将用户发来的消息传到吾来，机器人处理后，回调消息投递接口返回机器人的回复。

对接前提：
1. 调用方提供消息收发的渠道。
2. 渠道具有 WebSocket 能力。
3. 已经在吾来平台-渠道设置-开放平台(新版)设置了消息投递接口。
4. 已经在吾来机器人平台搭建并训练了机器人。

对接步骤：
1. 调用 user/create，传入 user_id， 创建用户；
2. 如果需要个性化回复，在此处调用 user/user-attribute/create 接口，传入 user_id 和该用户的用户属性；
3. 调用 msg/receive 将用户的消息传给机器人；
4. 吾来机器人会根据吾来平台上的配置回调消息投递接口，返回置信度最高的回复，同时返回0~10条相近的回复，
   按照置信度从高到低排序。调用方可根据自己的业务流程，依据置信度参数 score 的高低或者 is_send 的值，选择一条或多条回复。
5. 吾来平台会回调消息投递接口，将最终回复发给用户。
"""
import os

from wulaisdk.client import WulaiClient


pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")

client = WulaiClient(pubkey, secret, debug=False)

# 创建用户
resp_cu = client.create_user("test_user", nickname="测试用户")

# 添加属性值 - 根据需要操作
# user_attribute_user_attribute_value = [
#     {"user_attribute": {"id": "101343"}, "user_attribute_value": {"name": "新用户"}},
#     {"user_attribute": {"id": "101344"}, "user_attribute_value": {"name": "小区a"}},
# ]
# resp_crra = client.create_user_user_attribute("test_user", user_attribute_user_attribute_value)

# 消息传递给机器人
msg_body = {
    "text": {"content": "你好"}
}
third_msg_id = "aaa"
user_id = "test_user"
resp_gbr = client.receive_message(user_id, msg_body, third_msg_id)

# 需要调用方配置消息投递接口，详见CALLBACK.md
