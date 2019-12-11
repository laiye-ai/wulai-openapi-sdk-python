"""
六、知识库搭建
知识库搭建在大部分情况下可在吾来平台人工完成。如果项目需要不登录吾来平台的情况下就搭建和管理知识库，可以按照以下流程接入。

对接步骤：

创建知识点
1）调用 qa/knowledge-tags/list 接口，查询可用的知识点分类；
2）用 qa/knowledge-tag-knowledge/create 接口，创建知识点。
创建属性组
1）调用 user-attribute/list 接口，查询可用于定义属性组的用户属性；
2）调用 qa/user-attribute-group-items/create 接口，创建属性组。
创建属性组回复
1）调用 qa/user-attribute-group-items/list 接口，查询已有的属性组；
2）调用 qa/knowledge-items/list 接口，查询已有的知识点。
3）调用 qa/user-attribute-group-answer/create 接口，创建属性组回复。
"""
import os

from wulaisdk.client import WulaiClient

pubkey = os.getenv("PUBKEY", "")
secret = os.getenv("SECRET", "")

client = WulaiClient(pubkey, secret, debug=False)


def find_value_from_dict_array(li, search_key, value_key, reference):
    """
    在[{}, {}, ...]中找到合适的值
    :param li:
    :param search_key: 需要查询的key
    :param value_key: 目标值所在key
    :param reference: 对比值
    :return:
    """
    for di in li:
        if di[search_key] == reference:
            return di[value_key]
    return None


################
#  查询知识点分类
################
# 1. 获取parent_k_tag_id
page = 1
page_size = 30
resp_parent_tags = client.knowledge_tags(page, page_size)
parent_k_tag_id = resp_parent_tags.knowledge_tags[0].id
# 2. 获取所有子分类
resp_second_tags = client.knowledge_tags(page, page_size, parent_k_tag_id)
knowledge_tags = resp_second_tags.knowledge_tags
knowledge_tags_di = [r.to_dict() for r in knowledge_tags]
# 3. 找到需要的分类id
tag_name = "xxx"  # 需要添加知识点的分类名称
target_id = find_value_from_dict_array(knowledge_tags_di, "name", "id", tag_name)

# 创建知识点
knowledge_c = {
    "knowledge": {
        "status": True,
        "standard_question": "标准问",
        "respond_all": True,
        "maintained_by_user_attribute_group": True
    },
    "knowledge_tag_id": target_id
}

resp_knowledge_c = client.create_knowledge(knowledge_c)
knowledge_id = resp_knowledge_c.knowledge_tag_knowledge.knowledge.id

################
#   创建属性组
################
# 1.获取用户属性列表
resp_attributes = client.user_attributes(page, page_size)

# 2. 获取到属性id
attribute_id_1 = ""
attribute_id_2 = ""

# 3. 定义属性值
attribute_value_1 = ""
attribute_value_2 = ""

# 4. 定义属性组名称
attribute_group_name = ""

# 5. 创建属性组
user_attribute_group_item = {
    "user_attribute_user_attribute_value": [
        {
            "user_attribute": {"id": attribute_id_1},
            "user_attribute_value": {"name": attribute_value_1}
        },
        {
            "user_attribute": {"id": attribute_id_2},
            "user_attribute_value": {"name": attribute_value_2}
        }
    ],
    "user_attribute_group": {"name": attribute_group_name}
}
resp_cuagi = client.create_user_attribute_group_items(user_attribute_group_item)

################
#  创建属性组回复
################
# 1. 获取所有属性组
resp_attribute_groups = client.user_attribute_group_items(page, page_size)
# 2. 获取属性组id
attribute_group_id = ""
# 3. 获取所有知识点
resp_knowledge_items = client.knowledge_items(page, page_size)
# 4. 获取知识点id
n_knowledge_id = ""
# 5. 回复内容
msg_body = {
    "text": {
        "content": f"这是属性组回复的内容"
    }
}
# 6. 创建属性组回复
user_attribute_group_answer = {
    "answer": {
        "knowledge_id": n_knowledge_id,
        "msg_body": msg_body,
    },
    "user_attribute_group_id": attribute_group_id
}
resp_cuaga = client.create_user_attribute_group_answer(user_attribute_group_answer)
