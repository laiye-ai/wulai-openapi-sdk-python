"""
用户类api测试
"""
import os
import pytest

from wulaisdk.client import WulaiClient
from wulaisdk.exceptions import ClientException

pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")
log_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


#############################################################
#                          用户类
#############################################################
# createUser test
@pytest.mark.parametrize('debug,user_id,avatar_url,nickname,expected', [
    (True, "shierlou", "", "测试用户-shierlou", {}),
    (True, "shierlou", "", "", {}),
    (True, "test1", "", "", {}),
])
def test_create_user_normal_1(debug, user_id, avatar_url, nickname, expected):
    client = WulaiClient(pubkey, secret, debug=debug)
    resp = client.create_user(user_id, avatar_url, nickname)
    assert resp == expected


@pytest.mark.parametrize('debug,user_id,expected', [
    (True, "shierlou", {}),
    (True, "shierlou", {}),
])
def test_create_user_normal_2(debug, user_id, expected):
    client = WulaiClient(pubkey, secret, debug=debug)
    resp = client.create_user(user_id)
    assert resp == expected


@pytest.mark.parametrize('debug,user_id', [
    (True, ""),
    (False, 123),
])
def test_create_user_error(debug, user_id):
    client = WulaiClient(pubkey, secret, debug=debug)
    with pytest.raises(ClientException) as excinfo:
        client.create_user(user_id)
        assert excinfo.error_code == "SDK_INVALID_PARAMS"


# 获取用户属性列表
@pytest.mark.parametrize('filter, page, page_size', [
    (None, 1, 50),
    (None, 2, 30),
    ({"use_in_user_attribute_group": True}, 1, 30),
    ({"use_in_user_attribute_group": False}, 1, 30)
])
def test_user_attributes(filter, page, page_size):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.user_attributes(page, page_size, filter)
    assert resp


# 查询用户属性值
@pytest.mark.parametrize('user_id', [
    "shierlou"
])
def test_user_user_attribute(user_id):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.user_user_attribute(user_id)
    assert resp


# 给用户添加属性值
@pytest.mark.parametrize('user_attribute_user_attribute_value, user_id', [
    ([{"user_attribute": {"id": "101627"}, "user_attribute_value": {"name": "微博"}}], "shierlou"),
    ([{"user_attribute": {"id": "101629"}, "user_attribute_value": {"name": "老用户"}}], "shierlou"),
    ([
        {"user_attribute": {"id": "101627"}, "user_attribute_value": {"name": "微信"}},
        {"user_attribute": {"id": "101629"}, "user_attribute_value": {"name": "新用户"}}
    ], "shierlou"),
])
def test_create_user_attribute(user_attribute_user_attribute_value, user_id):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.create_user_attribute(user_attribute_user_attribute_value, user_id)
    assert 1


# createUserUserAttribute test
# 注：接口功能同上create_user_attribute，不小心创建重复
@pytest.mark.parametrize('user_id,user_attribute_user_attribute_value,expected', [
    ("shierlou", [
        {"user_attribute": {"id": "101343"}, "user_attribute_value": {"name": "新用户"}},
        {"user_attribute": {"id": "101344"}, "user_attribute_value": {"name": "小区a"}},
    ], {}),
])
def test_create_user_user_attribute_normal(user_id, user_attribute_user_attribute_value, expected):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.create_user_user_attribute(user_id, user_attribute_user_attribute_value)
    assert resp == expected


# 查询用户信息
@pytest.mark.parametrize('user_id', [
    "shierlou"
])
def test_get_user_normal(user_id):
    client = WulaiClient(pubkey, secret, debug=True)
    resp = client.get_user(user_id)
    assert resp.nickname
    assert resp.avatar_url


@pytest.mark.parametrize('user_id', [
    "shierlou111"
])
def test_get_user_error(user_id):
    client = WulaiClient(pubkey, secret, debug=True)
    with pytest.raises(ClientException) as excinfo:
        client.get_user(user_id)
        assert excinfo.error_code == "SDK_INVALID_PARAMS"


# 更新用户信息
@pytest.mark.parametrize('user_id, avatar_url, nickname', [
    ("test1", "https://www.baidu.com/img/bd_logo1.png", "测试用户1"),
    ("test1", None, None)
])
def test_update_user(user_id, avatar_url, nickname):
    client = WulaiClient(pubkey, secret, debug=True)
    client.update_user(user_id, avatar_url, nickname)
    resp = client.get_user(user_id)
    if avatar_url:
        assert resp.avatar_url == avatar_url
        assert resp.nickname == nickname
    else:
        assert resp.avatar_url
        assert resp.nickname
