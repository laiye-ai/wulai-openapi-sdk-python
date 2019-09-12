### 回调类接口实现


#### 消息路由
> 消息路由即 Webhook ，该 Web 服务需要开发者自己搭建，并且需要遵从开放平台预先定义好的输入输出。  
  机器人每次响应，吾来会把机器人回复内容、对话解析结果传给消息路由，
  调用方可以按需使或修改消息体内容达到影响机器人回复的目的  
  消息路由可视为：在获取机器人回复前（bot-response），对response的预处理。  
  在同步方式、异步方式中均可使用。

以tornado代码为例
```
class WebhookHandler(BaseRequestHandler):
    """
    吾来平台消息路由
    """

    async def post(self, *args, **kwargs):
        data = json.loads(self.request.body)

        # 消息路由处理
        # 回复列表
        suggested_response = data['suggested_response']
        # 转人工标志
        is_dispatch = data["is_dispatch"]
        
        for one in suggested_response:
            # do sth

        resp = {
            "is_dispatch": is_dispatch,
            "suggested_response": suggested_response
        }

        return self.write(resp)
```


#### 消息投递
> 调用方开发。如果机器人对接第三方渠道，机器人做出响应后，会调用消息投递接口，将消息投递到第三方渠道。

**注意**：
1) 此接口可保证至少投递一次（即服务质量QOS=At least once，不保证100%消息只投递一次）；
2) 此接口不能保证消息100%按照消息发送的顺序投递

**因此建议**：
1) 接入方根据msg_id做去重
2) 接入方根据msg_ts在客户端做重排序

以tornado为例  
该示例中消息投递接口直接对接websocket渠道。
```
class UserSocketHandler(tornado.websocket.WebSocketHandler):
    """
    客户端长连接, 处理接收和发送消息
    """
    async def ai_reply(self, data, user_id):
        """
        根据用户 ID 发送吾来回复消息给客户端
        """
        result = {
            'action': 'reply',
            'data': data
        }
        await self.write_message(result)
    # ...
    


class CallbackHandler(BaseHandler):
    """
    接收吾来平台回调, 返回信息给客户端
    """

    async def post(self, *args, **kwargs):
        data = json.loads(self.request.body)
        # do sth.
        # websocket服务
        await UserSocketHandler.ai_reply(content, user_id)
        self.write("success")
```