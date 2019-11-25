import os
import time
import pytest

from wulaisdk.client import WulaiClient
from wulaisdk.exceptions import ClientException


pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")
log_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


#############################################################
#                           统计类
#############################################################
# 添加用户满意度评价
# 步骤: 1. bot-response 2. sync 3. this api
@pytest.mark.parametrize('user_id, satisfaction', [
    ("shierlou", "THUMB_UP"),
    ("shierlou", "BAD_ANSWER"),
    ("shierlou", "WRONG_ANSWER"),
    ("shierlou", "REPORT")
])
def test_create_qa_satisfaction(user_id, satisfaction):
    client = WulaiClient(pubkey, secret, debug=True)

    # 获取机器人回复
    msg_body = {"text": {"content": "你好"}}
    resp_bot_response = client.get_bot_response(user_id, msg_body)
    bot = resp_bot_response.suggested_response[0].bot
    msg_body_response = resp_bot_response.suggested_response[0].response[0].msg_body.to_dict()

    # 同步发给用户的消息（机器人回复）
    msg_ts = str(int(time.time() * 1000))
    resp_sync = client.sync_message(user_id, msg_body_response, msg_ts, bot=bot.to_dict())

    # msg_id
    msg_id = resp_sync.msg_id
    # knowledge_id
    knowledge_id = bot.qa.knowledge_id

    resp = client.create_qa_satisfaction(msg_id, user_id, {"knowledge_id": str(knowledge_id)}, satisfaction)
    assert resp == {}


# 查询问答满意度评价统计列表（知识点粒度，日报）
@pytest.mark.parametrize('start_date, end_date, page, page_size', [
    ("20190930", "20191030", 1, 50),
    ("20190930", "20191030", 2, 20),
])
def test_stats_qa_satisfaction_daily_knowledges_normal(start_date, end_date, page, page_size):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.stats_qa_satisfaction_daily_knowledges(start_date, end_date, page, page_size)
    assert resp.to_dict()


@pytest.mark.parametrize('start_date, end_date, page, page_size', [
    ("20190830", "20191030", 1, 50),
    ("20190930", "20190830", 2, 20),
])
def test_stats_qa_satisfaction_daily_knowledges_error(start_date, end_date, page, page_size):
    client = WulaiClient(pubkey, secret, debug=True)
    with pytest.raises(ClientException) as excinfo:
        client.stats_qa_satisfaction_daily_knowledges(start_date, end_date, page, page_size)
        assert excinfo.error_code == "SDK_INVALID_PARAMS"


# 查询问答召回数统计列表（日报）
@pytest.mark.parametrize('start_date, end_date', [
    ("20190930", "20191030"),
])
def test_stats_qa_recall_daily_normal(start_date, end_date):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.stats_qa_recall_daily(start_date, end_date)
    assert resp.to_dict()


# 查询问答召回数统计列表（知识点粒度，日报）
@pytest.mark.parametrize('start_date, end_date, page, page_size', [
    ("20190930", "20191030", 1, 50),
    ("20190930", "20191030", 2, 20),
])
def test_stats_qa_recall_daily_knowledges_normal(start_date, end_date, page, page_size):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.stats_qa_recall_daily_knowledges(start_date, end_date, page, page_size)
    assert resp.to_dict()
