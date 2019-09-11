### 常用api

```
client = WulaiClient(pubkey, secret)
```


##### 1. 创建用户
> 创建用户后可以实现多轮对话机器人、从用户维度统计分析、吾来工作台人工收发消息、用户维护的消息记录查询与搜索等功能。  
在用户与机器人进行任何交互之前，都需要先创建用户。
```
client.create_user(user_id, avatar_url, nickname)
```

##### 2. 获取机器人回复
> 输入用户的文本消息内容，吾来机器人理解并做出响应，返回最合适的答复给用户。
```
client.get_bot_response(user_id, msg_body, extra)
```

##### 3. 获取关键字机器人回复
> 关键字机器人输入用户的文本消息内容，吾来机器人理解并做出响应，返回最合适的关键字机器人回复答复给用户。
```
client.get_keyword_bot_response(user_id, msg_body, extra)
```

##### 4. 获取问答机器人回复
> 问答机器人输入用户的文本消息内容，吾来机器人理解并做出响应，返回最合适的问答机器人回复答复给用户。
```
client.get_qa_bot_response(user_id, msg_body, extra)
```

##### 5. 获取任务机器人回复
> 任务机器人输入用户的文本消息内容，吾来机器人理解并做出响应，返回最合适的任务机器人回复答复给用户。
```
client.get_task_bot_response(user_id, msg_body, extra)
```

##### 6. 添加用户属性
> 该接口用于给用户添加或修改用户属性，包括预设属性和自定义属性。
```
client.create_user_user_attribute(user_id, user_attribute_user_attribute_value)
```

##### 7. 消息同步
> 同步发给用户的消息  
如果机器人接入第三方消息渠道，需要把发给用户的所有消息同步给吾来，这样才可以在吾来查看到全部消息记录。
```
client.sync_message(user_id, msg_body, msg_ts, extra)
```

##### 8. 接收用户消息
> 如果机器人接入第三方消息渠道，需要把用户发的所有消息同步给吾来，可以实现机器人全自动交互场景（参考异步基础对话、异步定制对话）。
```
client.receive_message(user_id, msg_body, third_msg_id, extra)
```

##### 9. 查询历史消息
> 获取与指定用户发生的历史对话消息。
```
client.get_message_history(user_id, num, direction, msg_id)
```
