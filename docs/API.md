### 常用api

```
client = WulaiClient(pubkey, secret)
```

### 用户类
##### 1. 创建用户
> 创建用户后可以实现多轮对话机器人、从用户维度统计分析、吾来工作台人工收发消息、用户维护的消息记录查询与搜索等功能。  
在用户与机器人进行任何交互之前，都需要先创建用户。
```
client.create_user(user_id, avatar_url, nickname)
```

##### 2. 查询用户信息
> 获取一个用户的详细信息。
```
client.get_user(user_id)
```

##### 3. 更新用户信息
> 更新用户昵称和头像地址。
```
client.update_user(user_id, avatar_url, nickname)
```

##### 4. 获取用户属性列表
> 该接口用于查询符合过滤条件的用户属性及其属性值。如果没有过滤条件，则返回所有用户属性及其属性值。
 当一个用户属性关联多个属性值时，会返回的user_attribute_user_attribute_values中有多组。
  比如：用户属性“性别”有属性值“男”，“女”。则接口返回的user_attribute_user_attribute_values有两组。
```
client.user_attributes(page, page_size, filter)
```

##### 5. 查询用户的属性值
> 查询一个用户的所有属性和属性值。
```
client.user_user_attribute(user_id)
```

##### 6. 给用户添加属性值
> 该接口用于给用户添加或修改用户属性，包括系统属性和临时属性。
```
client.create_user_attribute(user_attribute_user_attribute_value, user_id)
```


### 对话类
##### 1. 获取机器人回复
> 输入用户的文本消息内容，吾来机器人理解并做出响应，返回最合适的答复给用户。
```
client.get_bot_response(user_id, msg_body, extra)
```

##### 2. 获取关键字机器人回复
> 关键字机器人输入用户的文本消息内容，吾来机器人理解并做出响应，返回最合适的关键字机器人回复答复给用户。
```
client.get_keyword_bot_response(user_id, msg_body, extra)
```

##### 3. 获取问答机器人回复
> 问答机器人输入用户的文本消息内容，吾来机器人理解并做出响应，返回最合适的问答机器人回复答复给用户。
```
client.get_qa_bot_response(user_id, msg_body, extra)
```

##### 4. 获取任务机器人回复
> 任务机器人输入用户的文本消息内容，吾来机器人理解并做出响应，返回最合适的任务机器人回复答复给用户。
```
client.get_task_bot_response(user_id, msg_body, extra)
```

##### 5. 同步发给用户的消息
> 如果机器人接入第三方消息渠道，需要把发给用户的所有消息同步给吾来，这样才可以在吾来查看到全部消息记录。
如果需要使用满意度评价接口，则需要在调用本接口时传入机器人信息(bot)以及机器人回复的答案Id(answer_id)。
```
client.sync_message(user_id, msg_body, msg_ts, extra, answer_id, bot)
```

##### 6. 接收用户发的消息
> 如果机器人接入第三方消息渠道，需要把用户发的所有消息同步给吾来，可以实现机器人全自动交互场景（参考全自动接入方案）、人机协作方案）。调用本接口的前提是已经在吾来机器人平台的搭建并训练了机器人。
```
client.receive_message(user_id, msg_body, third_msg_id, extra)
```

##### 7. 查询历史消息
> 获取与指定用户发生的历史对话消息。
```
client.get_message_history(user_id, num, direction, msg_id)
```

##### 8. 给用户发消息
> 获取与指定用户发生的历史对话消息。
```
client.send_message(user_id, msg_body, quick_reply, similar_response, extra)
```

##### 9. 获取用户输入联想
> 在用户输入时提供相似知识点联想，减少用户的输入成本。
```
client.get_user_suggestion(user_id, query)
```


### 知识点类
##### 1. 创建知识点
> 该接口可创建知识点，并同时定义知识点的标准问、是否使用属性组、生效状态、以及知识点所属分类。  
注:只有当一个知识点分类已经在吾来平台中创建后，才可在该接口中传入其id。如果知识点分类id尚未在系统中创建，则无法成功创建知识点
```
client.create_knowledge(knowledge_tag_knowledge)
```

##### 2. 更新知识点
> 该接口可更新知识点相关信息，具体内容包含知识点的标准问、是否使用属性组、生效状态、以及知识点所属分类。
```
client.update_knowledge(knowledge)
```

##### 3. 删除知识点
> 该接口可删除一个知识点，如果一个知识点关联了相似问、或未删除的属性组回复，则一并删除
```
client.delete_knowledge(knowledge_id)
```

##### 4. 查询知识点列表
> 该接口可返回知识点相关信息，具体内容包含知识点所在分类、知识点标准问以及相似问。  
返回的知识点范围为：调用时使用的开放平台Pubkey所属的项目(APP)中的所有知识点。
```
client.knowledge_items(page, page_size)
```

##### 5. 查询知识点分类列表
> 该接口可更新知识点相关信息，具体内容包含知识点的标准问、是否使用属性组、生效状态、以及知识点所属分类。
```
client.knowledge_tags(page, page_size, parent_k_tag_id)
```

##### 6. 创建相似问
> 该接口可创建相似问，具体内容包括相似问所关联的知识点、和相似问的内容。  
注:只有当知识点id已经在吾来平台中创建后，才可通过该接口创建相似问。如果知识点id尚未在系统中创建，则无法成功创建相似问。
```
client.create_similar_question(similar_question)
```

##### 7. 更新相似问
> 该接口可创建相似问，具体内容包括相似问所关联的知识点、和相似问的内容。  
注:只有当知识点id已经在吾来平台中创建后，才可通过该接口创建相似问。如果知识点id尚未在系统中创建，则无法成功创建相似问。
```
client.update_similar_question(similar_question)
```

##### 8. 删除相似问
> 该接口可删除相似问。
```
client.delete_similar_question(similar_id)
```

##### 9. 查询相似问列表
> 该接口可返回相似问的相关信息，包括相似问所关联的知识点、和相似问的内容。
 调用方可选择根据知识点查询（在请求参数中传入知识点id）、根据相似问查询（在请求参数中传入相似问id）、
 或者查询所有知识点问题（在请求参数中不传入任何filter）。
```
client.similar_questions(page, page_size, knowledge_id, similar_question_id)
```

##### 10. 创建属性组
> 该接口用于创建属性组，具体内容包括属性组名称，及构成该属性组的用户属性和属性值。
```
client.create_user_attribute_group_items(user_attribute_group_item)
```

##### 11. 更新属性组
> 该接口用于更新属性组，具体内容包括属性组名称，及构成该属性组的用户属性和属性值。
```
client.update_user_attribute_group_items(user_attribute_group_item)
```

##### 12.查询属性组及属性列表
> 该接口可返回属性组相关信息，包括属性组名称、属性组内所包含的属性和属性值。  
返回的范围为：调用时使用的开放平台Pubkey所属的项目(APP)中的所有属性组。
```
client.user_attribute_group_items(page, page_size)
```

##### 13. 创建属性组回复
> 该接口可创建属性组回复，具体内容包括属性组回复所关联的知识点、和属性组回复的消息内容。  
注:只有当知识点id已经在吾来平台中创建后，才可通过该接口创建属性组回复。如果知识点id尚未在系统中创建，则无法成功创建属性组回复
```
client.create_user_attribute_group_answer(user_attribute_group_answer)
```

##### 14. 更新属性组回复
> 该接口可更新属性组回复，具体内容包括属性组回复所关联的知识点、和属性组回复的消息内容。  
注:如需更新知识点的通用答案（不区分属性组），则 user_attribute_group_id 传入0.
```
client.update_user_attribute_group_answer(user_attribute_group_answer)
```

##### 15. 查询属性组回复列表
> 该接口可返回属性组回复相关信息，包括属性组回复所关联的知识点、和属性组回复的消息内容。调用方可选择根据知识点查询（在请求参数中传入知识点id）、根据属性组查询（在请求参数中传入属性组id）、
或者查询所有属性组回复（在请求参数中不传入任何filter）。
```
client.user_attribute_group_answers(page, page_size, kn_filter)
```

##### 16. 删除属性组回复
> 该接口用于删除一条属性组的回复。
```
client.delete_user_attribute_group_answer(uaga_id)
```

### 统计类
##### 1. 添加用户满意度评价
> 该接口用于写入用户的满意度评价。
```
client.create_qa_satisfaction(msg_id, user_id, bot_id, satisfaction)
```

##### 2. 查询问答满意度评价统计列表（知识点粒度，日报）
> 该接口可按照开始和结束日期查询每个知识点每天的满意度统计。满意度数据分为：点赞、答案不满意、答非所问三类。  
注:开始时间和结束时间相距不能超过30天。
```
client.stats_qa_satisfaction_daily_knowledges(start_date, end_date, page, page_size)
```

##### 3. 查询问答召回数统计列表（日报）
> 该接口可按照开始和结束日期查询每天的接收消息总数和召回总数。  
注:开始时间和结束时间相距不能超过30天。
```
client.stats_qa_recall_daily(start_date, end_date)
```

##### 4. 查询问答召回数统计列表（知识点粒度，日报）
> 该接口可按照开始和结束日期查询每个知识点每天的召回数统计。  
注:开始时间和结束时间相距不能超过30天。
```
client.stats_qa_recall_daily_knowledges(start_date, end_date, page, page_size)
```

### 词库管理类
##### 1. 查询全部实体概要
> 查询全部实体的概要，包括实体ID、实体名称和实体类型。
```
client.dictionary_entities(page, page_size)
```

##### 2. 查询专有词汇列表
> 该接口用于查询所有的专有词汇，包括定义专有词汇的id、名称和同义词。
```
client.dictionary_terms(page, page_size)
```

##### 3. 创建专有词汇
> 该接口用于创建专有词汇，包括定义专有词汇的名称和同义词。
```
client.create_dictionary_term(term_item)
```

##### 4. 更新专有词汇
> 该接口可删除相似问。
```
client.update_dictionary_term(term_item)
```

##### 5. 删除专有词汇
> 该接口用于删除一条专有词汇。
```
client.delete_dictionary_term(term_id)
```

##### 6. 查询一个实体详情
> 查询一个实体的详情，包括实体ID、实体名称、实体类型和实体值。
```
client.dictionary_entity(entity_id)
```

##### 7. 创建枚举实体
> 创建一个枚举实体。  
注：枚举实体的实体值需要通过「创建枚举实体值」接口创建。
```
client.create_dictionary_entity_enumeration(enum_entity)
```

##### 8. 创建枚举实体值
> 给一个枚举实体添加实体值，包括标准值及其相似说法。
```
client.create_dictionary_entity_enumeration_value(entity_id, value)
```

##### 9. 删除枚举实体值
> 删除枚举实体的一个实体值，或实体值的若干相似说法。
```
client.delete_dictionary_entity_enumeration_value(entity_id, value)
```

##### 10. 创建意图实体
> 创建一个意图实体，及其标准值。  
注：意图实体的相似说法需要通过「创建意图实体值相似说法」接口创建。
```
client.create_dictionary_entity_intent(intent_entity)
```

##### 11. 创建意图实体值相似说法
> 给一个意图实体添加相似说法。
```
client.create_dictionary_entity_intent_value(entity_id, synonyms)
```

##### 12. 删除意图实体值相似说法
> 删除意图实体值相似说法
```
client.delete_dictionary_entity_intent_value(entity_id, synonyms)
```

##### 13. 删除实体
> 删除一个实体。  
注：预设实体不可删除。
```
client.delete_dictionary_entity(entity_id)
```

### 自然语言处理类
##### 1. 实体抽取
> 该接口用于实体抽取。
```
client.entities_extract(query)
```

##### 2. 分词&词性标注
> 该接口用于分词以及词性标注。
```
client.tokenize(query)
```

### 任务类
##### 1. 查询场景列表
> 查询任务对话中的所有场景。
```
client.scenes()
```

##### 2. 创建场景
> 创建任务对话中的一个场景。
```
client.create_scene(scene)
```

##### 3. 更新场景
> 更新任务对话中的一个场景。
```
client.update_scene(scene)
```

##### 4. 删除场景
> 删除任务对话中的一个场景。
```
client.delete_scene(scene_id)
```

##### 5. 查询意图列表
> 查询一个场景下的所有意图。
```
client.intents(scene_id)
```

##### 6. 创建意图
> 创建场景下的一个意图。  
注: 只有当一个场景已经在吾来平台中创建后，才可在当前接口中传入其ID。如果场景ID尚未创建，则无法成功创建意图。
```
client.create_intent(intent)
```

##### 7. 更新意图
> 更新场景下的一个意图。
```
client.update_intent(intent)
```

##### 8. 删除意图
> 删除场景下的一个意图。
```
client.delete_intent(intent_id)
```

##### 9. 查询触发器列表
> 查询一个意图中的所有触发器内容。
```
client.intent_triggers(intent_id, page, page_size)
```

##### 10. 创建触发器
> 创建一条触发器内容。触发器的文本匹配模式可以选择：完全匹配的关键词，包含匹配的关键词，或者相似说法。
```
client.create_intent_trigger(intent_trigger)
```

##### 11. 更新触发器
> 更新一条触发器内容。
```
client.update_intent_trigger(intent_trigger)
```

##### 12. 删除触发器
> 删除一条触发器内容。
```
client.delete_intent_trigger(intent_trigger_id)
```

##### 13. 查询词槽列表
> 查询一个场景下的所有词槽ID和词槽名称。
```
client.slots(scene_id, page, page_size)
```

##### 14. 创建词槽
> 创建词槽，包括设置词槽是否允许整句填槽。  
注：整句填槽指的是，当未识别到引用实体时，将用户的整句话填充到词槽。
```
client.create_slot(slot)
```

##### 15. 更新词槽
> 更新词槽。
```
client.update_slot(slot)
```

##### 16. 查询词槽
> 查询一个词槽的详情。
```
client.get_slot(slot_id)
```

##### 17. 删除词槽
> 删除词槽。
```
client.delete_slot(slot_id)
```

##### 18. 查询词槽数据来源
> 查询一个词槽的所有数据来源。
```
client.slot_data_source(slot_id)
```

##### 19. 创建词槽数据来源
> 创建词槽数据来源即定义词槽的引用实体，将实体与词槽关联起来。  
注：必须先创建词槽和实体后，才可以创建词槽数据来源。
```
client.create_slot_data_source(data_source)
```


##### 20. 删除词槽数据来源
> 删除词槽数据来源。
```
client.delete_slot_data_source(slot_data_source_id)
```

##### 21. 查询消息发送单元
> 该接口用于分词以及词性标注。
```
client.inform_block(block_id)
```

##### 22. 创建消息发送单元
> 创建一个消息发送单元。
```
client.create_inform_block(block)
```

##### 23. 更新消息发送单元
> 更新一个消息发送单元。
```
client.update_inform_block(block)
```

##### 24. 查询询问填槽单元
> 查询一个询问填槽单元的详情，包括单元设置、单元回复、该单元与其他单元的跳转关系等。  
注：必须先创建一个词槽，才可以在单元中使用它作为关联词槽。
```
client.request_block(block_id)
```

##### 25. 创建询问填槽单元
> 创建一个询问填槽单元。
```
client.create_request_block(block)
```

##### 26. 更新询问填槽单元
> 更新一个询问填槽单元。  
注：必须先创建一个词槽，才可以在单元中使用它作为关联词槽。
```
client.update_request_block(block)
```

##### 27. 创建单元内回复
> 给询问填槽单元或消息发送单元添加一条回复。
```
client.create_block_response(response)
```

##### 28.  更新单元内回复
> 给询问填槽单元或消息发送单元更新一条回复。
```
client.update_block_response(response)
```

##### 29. 删除单元内回复
> 删除一条单元内回复。
```
client.delete_block_response(response_id)
```

##### 30. 查询意图终点单元
> 查询一个意图终点单元的详情。
```
client.end_block(block_id)
```

##### 31. 创建意图终点单元
> 创建一个意图终点单元。  
注：意图终点单元如果要跳转到一个指定意图，该意图必须先被创建。
```
client.create_end_block(block)
```

##### 32. 更新意图终点单元
> 更新一个意图终点单元。
```
client.update_end_block(block)
```

##### 33. 查询单元列表
> 查询意图里的所有单元。
```
client.blocks(intent_id, page, page_size)
```

##### 34. 创建单元关系
> 创建单元与单元之间的跳转关系，包括当前单元、下一个单元、以及跳转条件。
```
client.create_block_relation(relation)
```

##### 35. 删除单元关系
> 删除一条单元与单元之间的跳转关系。
```
client.delete_block_relation(relation_id)
```

##### 36. 删除单元
> 删除一个对话单元，支持所有类型的单元。
```
client.delete_block(block_id)
```

##### 37. 查询任务待审核消息列表
> 查询触发意图的待审核消息列表。
```
client.intent_trigger_learning(page, page_size)
```

##### 38. 删除任务待审核消息
> 删除一条触发意图的待审核消息。
```
client.delete_intent_trigger_learning(msg_id)
```

##### 39. 更新意图状态
> 将意图生效或者下线，同时需要指定意图的第一个单元。
```
client.update_intent_status(status, first_block_id, intent_id)
```
