"""
对话类api测试
"""
import os
import time
import pytest

from wulaisdk.client import WulaiClient
from wulaisdk.response.category_talk import BotResponse
from wulaisdk.response.msg_body import MsgBody


pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")
log_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


#############################################################
#                          对话类
#############################################################
# getBotResponse test
@pytest.mark.parametrize('user_id,msg_body,extra', [
    ("shierlou", {"text": {"content": "你好"}}, "this is extra string")
])
def test_get_bot_response_normal(user_id, msg_body, extra):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.get_bot_response(user_id, msg_body, extra)
    assert resp.suggested_response[0].response[0].msg_body.text.content == '你好，有什么可以为你服务的吗？(*╹▽╹*)'


# getBotResponse for image test
@pytest.mark.parametrize('user_id,msg_body', [
    ("shierlou", {"text": {"content": "图片如何回复"}})
])
def test_get_bot_response_image(user_id, msg_body):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.get_bot_response(user_id, msg_body)
    assert isinstance(resp.suggested_response[0].response[0].msg_body.image.resource_url, str)


# getKeyWordBotResponse test
@pytest.mark.parametrize('user_id,msg_body,expected', [
    ("shierlou", {"text": {"content": "关键词测试"}}, "哈哈哈，这是关键词😃")
])
def test_get_keyword_bot_response_normal(user_id, msg_body, expected):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.get_keyword_bot_response(user_id, msg_body)
    assert resp.to_dict()["keyword_suggested_response"][0]["response"][0]["msg_body"]["text"]["content"] == expected
    assert resp.keyword_suggested_response[0].response[0].msg_body.text.content == expected


# getQABotResponse test
@pytest.mark.parametrize('user_id,msg_body,extra,expected', [
    ("shierlou", {"text": {"content": "吃了吗"}}, "this is extra string", "服务你第一，吃饭第二，请问有什么可以帮助你的吗？")
])
def test_get_qa_bot_response_normal(user_id, msg_body, extra, expected):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.get_qa_bot_response(user_id, msg_body, extra)
    assert resp.to_dict()["qa_suggested_response"][0]["response"][0]["msg_body"]["text"]["content"] == expected
    assert resp.qa_suggested_response[0].response[0].msg_body.text.content == expected


# getQABotResponse for image test
@pytest.mark.parametrize('user_id,msg_body,extra', [
    ("shierlou", {"text": {"content": "图片如何回复"}}, "this is extra string")
])
def test_get_qa_bot_response_image(user_id, msg_body, extra):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.get_qa_bot_response(user_id, msg_body, extra)
    assert isinstance(resp.qa_suggested_response[0].response[0].msg_body.image.resource_url, str)


# getTaskBotResponse test
@pytest.mark.parametrize('user_id,msg_body,extra', [
    ("shierlou", {"text": {"content": "我想查尺码"}}, "this is extra string")
])
def test_get_task_bot_response_normal(user_id, msg_body, extra):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.get_task_bot_response(user_id, msg_body, extra)
    assert "text" in resp.to_dict()["task_suggested_response"][0]["response"][0]["msg_body"].keys()
    assert isinstance(resp.task_suggested_response[0].response[0].msg_body.text.content, str)


# syncMessage test
@pytest.mark.parametrize('user_id,msg_body,msg_ts', [
    ("shierlou", {"text": {"content": "测试message_sync"}}, str(int(time.time() * 1000)))
])
def test_sync_message(user_id, msg_body, msg_ts):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.sync_message(user_id, msg_body, msg_ts)
    assert "msg_id" in resp.to_dict()
    assert isinstance(resp.msg_id, str)


# receiveMessage test
@pytest.mark.parametrize('user_id,msg_body', [
    ("shierlou", {"text": {"content": "测试receive_message"}})
])
def test_receive_message(user_id, msg_body):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.receive_message(user_id, msg_body)
    assert "msg_id" in resp.to_dict()
    assert isinstance(resp.msg_id, str)


# getMessageHistory test
@pytest.mark.parametrize('user_id,num', [
    ("shierlou", 50)
])
def test_message_history(user_id, num):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.get_message_history(user_id, num)
    assert resp.to_dict()
    assert isinstance(resp.msg[0].user_info.nickname, str)
    assert isinstance(resp.msg[0].msg_body.to_dict(), dict)
    msg_body = resp.msg[0].msg_body
    if hasattr(msg_body, "text"):
        assert isinstance(msg_body.text.content, str)
    elif hasattr(msg_body, "image"):
        assert isinstance(msg_body.image.resource_url, str)


# bot-response wrapper test
@pytest.mark.parametrize('body', [
    {"msg_id": "123", "test": "test", "is_dispatch": False, "suggested_response": [], "extra": ""}
])
def test_err_response(body):
    assert BotResponse.from_dict(body)


# msg_body wrapper test
@pytest.mark.parametrize('body', [
    {"text": {"content": "hhhh"}},
    {"image": {"resource_url": "hhhh"}},
    {"test": {"test": "test"}},
])
def test_err_response(body):
    assert MsgBody.from_dict(body)


# 给用户发消息
@pytest.mark.parametrize('user_id, msg_body, quick_reply, similar_response, extra', [
    ("shierlou", {"text": {"content": "测试给用户发消息"}}, None, None, None),
    ("shierlou", {"text": {"content": "测试给用户发消息2"}}, ["快捷回复1", "快捷回复2"], {
        "source": "QA_BOT",
        "detail": {
            "qa": {
                "knowledge_id": "",
                "standard_question": "",
                "question": "",
                "is_none_intention": False
            }
        }
    }, ""),
])
def test_send_message(user_id, msg_body, quick_reply, similar_response, extra):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.send_message(user_id, msg_body, quick_reply, similar_response, extra)
    assert resp.msg_id


# 获取用户输入联想
@pytest.mark.parametrize('user_id, query', [
    ("shierlou", "你好"),
])
def test_send_message(user_id, query):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.get_user_suggestion(user_id, query)
    user_suggestiont = resp.user_suggestions[0]
    assert user_suggestiont.suggestion


#############################################################
#                   reset task bot
#############################################################
@pytest.mark.parametrize('user_id,msg_body,extra', [
    ("shierlou", {"text": {"content": "/restart"}}, "this is extra string")
])
def test_reset_task(user_id, msg_body, extra):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.get_bot_response(user_id, msg_body, extra)
    assert isinstance(resp.suggested_response[0].response[0].msg_body.text.content, str)
