### version 1.1.9
#### updated 20200227
1. WulaiClient类配置参数中新增global_timeout，默认为5s，是全局的超时时间配置。该参数可被具体的api下的timeout参数重置。
2. 更新api使用文档，提示global_timeout及timeout的配置方式。

### version 1.1.8
#### updated 20200212
1. 新增5个api："创建知识点分类、更新知识点分类、删除知识点分类、批量添加知识点列表、更新机器人回复配置"
2. 更新api：查询知识点列表 - 传参新增filter

### version 1.1.7
#### updated 20191220
1. 新增5个api："导入待聚类语料、清空待聚类语料、发起聚类、获取聚类结果列表、删除聚类结果"
2. msg_body添加新格式：图文消息（rich_text），事件消息（event）

### version 1.1.6
#### updated 20191211
1. 新增5个api："查询用户信息、更新用户信息、获取用户输入联想、给用户发消息、删除知识点"
2. "知识库搭建"场景更新
3. "满意度收集"场景更新

### version 1.1.5
#### updated 20191206
1. 更新自然语言处理类api
2. headers中增加版本信息
3. 更新任务类api

### version 1.1.4
#### updated 20191125
1. 更新词库管理类api

### version 1.1.3
#### updated 20191106
1. 更新统计类相关api
2. get_bot_response/get_keyword_bot_response/get_qa_bot_response/get_task_bot_response api返回参数中增加answer_id
3. sync_message api传入参数中增加answer_id, bot

### version 1.1.2
#### updated 20191030  
1. 更新知识点类相关api  
2. 补全用户类api
