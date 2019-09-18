"""
基础对话场景


实现效果：发送消息给机器人，得到相应回复。

对接前提：
1. 调用方提供接入机器人的渠道。
2. 已经在吾来机器人平台搭建并训练了机器人。

对接步骤：
1. 调用 user/create 接口，传入 user_id，创建用户；
2. 调用 msg/bot-response 接口，传入用户消息和 user_id；
3. 机器人会返回1~10条可能的回复，按照置信度从高到低排序。
   调用方可根据自己业务需要，依据置信度参数 score 的高低或者 is_send 的值，选择一条或多条回复。
"""
import os

from wulaisdk.client import WulaiClient


pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")

client = WulaiClient(pubkey, secret, debug=False)

# 创建用户
resp_cu = client.create_user("test_user", nickname="测试用户")

# 获取回复
msg_body = {
    "text": {"content": "你好"}
}
resp_gbr = client.get_bot_response("test_user", msg_body)
