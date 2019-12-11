"""
七、满意度收集
每次回复时让用户添加满意度评价，之后一次性获取统计值。

对接步骤：

1. 调用获取机器人回复接口（v2/msg/bot-response），获取返回字段中的 bot 和knowledge_id；

2. 调用同步发给用户的消息接口（v2/msg/sync），传入步骤1中的 bot，同时获取返回字段中的 msg_id；

3. 调用添加用户满意度评价接口（v2/qa/satisfaction/create），传入步骤1中获得的 knowledge_id 和步骤2中获得的 msg_id。

4. 调用查询问答满意度评价统计列表（知识点粒度，日报）（v2/stats/qa/satisfaction/daily/knowledge/list），
传入开始时间和结束时间（开始时间和结束时间相距不能超过30天）并获得该时间段内的满意度统计值。
"""
import os
import time

from wulaisdk.client import WulaiClient


pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")

client = WulaiClient(pubkey, secret, debug=False)

# 1. 获取机器人回复
user_id = "test_user"
msg_body = {
    "text": {
        "content": "你好"
    }
}
resp = client.get_bot_response(user_id, msg_body)
bot = resp.suggested_response[0].bot.to_dict()
msg_body_response = resp.suggested_response[0].response[0].msg_body.to_dict()

# 2. 同步用户消息给吾来
msg_ts = str(int(time.time() * 1000))
resp_sync = client.sync_message(user_id, msg_body_response, msg_ts, bot=bot.to_dict())

# msg_id
msg_id = resp_sync.msg_id
# knowledge_id
knowledge_id = bot.qa.knowledge_id
# 满意度评价
satisfaction = "THUMB_UP"

# 3. 添加用户满意度评价
resp = client.create_qa_satisfaction(msg_id, user_id, {"knowledge_id": str(knowledge_id)}, satisfaction)

page = 1
page_size = 50
start_date = "20190930"
end_date = "20191030"
# 4. 调用查询问答满意度评价统计列表（知识点粒度，日报）
resp_stats = client.stats_qa_satisfaction_daily_knowledges(start_date, end_date, page, page_size)
