"""
基础对话场景
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
