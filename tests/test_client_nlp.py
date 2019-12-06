import os
import pytest

from wulaisdk.client import WulaiClient


pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")
log_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


#############################################################
#                       自然语言处理类
#############################################################
# 实体抽取测试
@pytest.mark.parametrize('query', [
    '灵刻车型有悦翔V5，江南TT和逸动',
    '我的ip地址是180.167.137.10',
])
def test_entities_extract(query):
    client = WulaiClient(pubkey, secret, debug=True)

    resp = client.entities_extract(query)
    assert resp.to_dict()
    for entity in resp.entities:
        if hasattr(entity.entity, "system_entity"):
            assert entity.entity.system_entity.standard_value
        elif hasattr(entity.entity, "enumeration_entity"):
            assert entity.entity.enumeration_entity.standard_value
        elif hasattr(entity.entity, "regex_entity"):
            assert entity.entity.regex_entity.name
        else:
            # error
            assert False


# 分词&词性标注
@pytest.mark.parametrize('query', [
    '灵刻车型有悦翔V5，江南TT和逸动',
    '我的ip地址是180.167.137.10',
])
def test_tokenize(query):
    client = WulaiClient(pubkey, secret, debug=True)

    resp = client.tokenize(query)
    assert resp.tokens[0].text
