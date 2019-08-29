"""
个性化对话场景
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
