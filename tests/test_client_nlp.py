import os
import pytest
import random

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


# 导入待聚类语料
@pytest.mark.parametrize('queries', [
    ['今天天气怎么样', '今天是晴天', '今天吃什么', '你好', '你真棒'],
    ['教练我想打篮球', '武磊牛逼', '湖人输了', '你看nba吗', '今天天气不错'],
])
def test_mining_upload(queries):
    client = WulaiClient(pubkey, secret, debug=True)

    resp = client.mining_upload(queries)
    assert resp.succeeded_count or resp.duplicated_count


# 发起聚类
def test_mining_execute():
    client = WulaiClient(pubkey, secret, debug=True)

    resp = client.mining_execute()
    assert resp.status


# 获取聚类结果列表
def test_mining_result():
    client = WulaiClient(pubkey, secret, debug=True)

    resp = client.mining_result(1, 50)
    # 聚类中
    if resp.status == "MINING_STATUS_IN_PROGRESS":
        assert 1
    # 聚类结束
    else:
        if resp.page_count:
            sentence_ids = []
            for cluster in resp.clusters:
                for sentence in cluster.sentences:
                    sentence_ids.append(sentence.id)
            del_id = random.choice(sentence_ids)
            # 删除聚类结果
            client.delete_mining_sentence(del_id)


# 清空待聚类语料
def test_mining_empty():
    client = WulaiClient(pubkey, secret, debug=True)

    client.mining_empty()
