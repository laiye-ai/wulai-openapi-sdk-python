import time
import uuid
import hashlib
import logging

from wulaisdk.http import BaseRequest
from wulaisdk import http_codes
from wulaisdk.request import CommonRequest
from wulaisdk.exceptions import ServerException, ClientException, ERR_INFO
from wulaisdk.response import BotResponse

from requests.exceptions import ConnectionError, ConnectTimeout


DEBUG = False

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.addHandler(handler)


class WulaiClient:
    def __init__(self, pubkey: str, secret: str, endpoint: str="https://openapi.wul.ai",
                 api_version: str="v2", debug: bool=False, pool=None, pool_connections: int=10, pool_maxsize: int=10,
                 max_retries: int=3):
        """
        client
        :param pubkey:
        :param secret:
        :param endpoint:
        :param api_version:
        :param debug:
        :param pool: connection pool. Each client instance has its own pool by default.
        Also you could create one on 'connection_pool_init' method and pass in arguments if you wanna a global pool.
        :param pool_connections:
        :param pool_maxsize:
        :param max_retries:
        """
        self.pubkey = pubkey
        self.secret = secret
        self.endpoint = endpoint
        self.api_version = api_version
        self.pool_connections = pool_connections
        self.pool_maxsize = pool_maxsize
        self.max_retries = max_retries
        self._http = pool or self.connection_pool_init(self.endpoint, self.pool_connections, self.pool_maxsize,
                                                       self.max_retries)
        global DEBUG
        DEBUG = debug
        self.prepare_request()

    def prepare_request(self):
        self.check_api_version()
        self.logger_level_init()

    @staticmethod
    def connection_pool_init(endpoint, pool_connections, pool_maxsize, max_retries):
        pool = BaseRequest(endpoint=endpoint, pool_connections=pool_connections,
                           pool_maxsize=pool_maxsize, max_retries=max_retries)
        return pool

    @staticmethod
    def logger_level_init():
        global logger
        if DEBUG:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.ERROR)

    @staticmethod
    def add_logger_handler(log_handler):
        global logger
        logger.addHandler(log_handler)

    def check_api_version(self):
        if self.api_version not in ["v1", "v2"]:
            raise ClientException("SDK_INVALID_API_VERSION", ERR_INFO["SDK_INVALID_API_VERSION"])

    def make_authentication(self, pubkey, secret):
        headers = {}
        timestamp = str(int(time.time()))
        nonce = uuid.uuid4().hex
        sign = hashlib.sha1((nonce + timestamp + secret).encode("utf-8")).hexdigest()
        data = {
            "pubkey": pubkey,
            "sign": sign,
            "nonce": nonce,
            "timestamp": timestamp
        }
        for k, v in data.items():
            headers["Api-Auth-" + k] = v
        return headers

    def check_request(self, request):
        if not isinstance(request, CommonRequest):
            raise ClientException("SDK_INVALID_REQUEST", ERR_INFO["SDK_INVALID_REQUEST"])

    def get_url(self, request):
        url = self.endpoint + "/" + self.api_version + request.action
        return url

    def response_wrapper(self, response):
        js = None
        exception = None
        if response is not None and response.status_code == http_codes.OK:
            try:
                js = response.json()
            except Exception:
                raise ClientException("SDK_RESPONSE_ERROR", "Please retry")
        elif response is not None and response.status_code >= http_codes.PARAMS_ERROR:
            try:
                err_msg = response.json()["message"]
            except Exception:
                err_msg = ""
            if response.status_code == 400:
                exception = ClientException("SDK_INVALID_PARAMS", err_msg or ERR_INFO["SDK_INVALID_PARAMS"])
            elif response.status_code == 401:
                exception = ClientException("SDK_INVALID_CREDENTIAL", ERR_INFO["SDK_INVALID_CREDENTIAL"])
            elif response.status_code == 405:
                exception = ClientException("SDK_METHOD_NOT_ALLOW", ERR_INFO["SDK_METHOD_NOT_ALLOW"])
            else:
                if not err_msg:
                    try:
                        err_msg = response.text
                    except Exception:
                        err_msg = "Sth error"
                exception = ServerException("SDK_UNKNOWN_SERVER_ERROR",
                                            err_msg,
                                            response.status_code)
        return js, exception

    def handle_single_request(self, request):
        self.check_request(request)
        url = self.get_url(request)
        auth_headers = self.make_authentication(self.pubkey, self.secret)
        request.update_headers(auth_headers)

        method = request.opts.get("method", "POST")
        timeout = request.opts.get("timeout", 3)
        logger.debug("Request received. Action: {}. Endpoint: {}. Params: {}. Opts: {}".format(
            request.action, self.endpoint, request.params, request.opts))

        try:
            if method.upper() == "POST":
                resp = self._http.post(url, request.params, request.headers, timeout)
            elif method.upper() == "GET":
                resp = self._http.get(url, request.params, request.headers, timeout)
            else:
                logger.error("SDK_METHOD_NOT_ALLOW: {}. method: {}".format(
                    ERR_INFO["SDK_METHOD_NOT_ALLOW"], method.upper()))
                raise ClientException("SDK_METHOD_NOT_ALLOW", ERR_INFO["SDK_METHOD_NOT_ALLOW"])
        except IOError as e:
            logger.error("HttpError occurred. Action:{} Version:{} ClientException:{}".format(
                request.action, self.api_version, str(e)))
            raise ClientException("SDK_HTTP_ERROR", str(e))
        except (ConnectTimeout, ConnectionError) as e:
            logger.error("HttpError occurred. Action:{} Version:{} ClientException:{}".format(
                request.action, self.api_version, str(e)))
            raise ClientException("SDK_SERVER_UNREACHABLE", str(e))
        return self.response_wrapper(resp)

    def process_common_request(self, request):
        retries = request.opts.get("retry", 0)
        while True:
            body, exception = self.handle_single_request(request)
            if body is not None:
                retries = -1
            else:
                retries -= 1
                logger.debug("Retry needed. Action: {}. Number of remaining retries: {}".format(
                    request.action, retries))
            if retries <= 0:
                break
        if exception:
            logger.error("{}:{}. Action:{} Version:{} Exception:".format(
                exception.error_code, exception.error_msg, request.action, self.api_version))
            raise exception
        logger.debug("Response received. Action: {}. Response-body: {}".format(request.action, body))
        return body

    @staticmethod
    def opts_create(di: dict):
        opts = {
            "method": di.get("method", "POST"),
            "retry": di.get("retry", 2),
            "timeout": di.get("timeout", 3)
        }
        return opts

    def create_user(self, user_id: str, avatar_url: str="", nickname: str="", **kwargs):
        """
        创建用户
        创建用户后可以实现多轮对话机器人、从用户维度统计分析、吾来工作台人工收发消息、用户维护的消息记录查询与搜索等功能。
        在用户与机器人进行任何交互之前，都需要先创建用户。
        :param user_id:	str (用户id作为用户的唯一识别。如果调用方客户端用户没有唯一标识，尽量通过其他标识来唯一区分用户，如设备号)[ 1 .. 128 ] characters
        :param avatar_url: 	str (用户头像地址。用户头像会展示在吾来SaaS的用户列表、消息记录等任何展示用户信息的地方) <= 512 characters
        :param nickname: str (用户昵称)
        :return:
        """
        params = {
            "user_id": user_id,
            "avatar_url": avatar_url,
            "nickname": nickname
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/user/create", params, opts)
        body = self.process_common_request(request)
        return body

    def get_bot_response(self, user_id: str, msg_body: dict, extra: str="", **kwargs):
        """
        获取机器人回复
        输入用户的文本消息内容，吾来机器人理解并做出响应，返回最合适的答复给用户。
        :param user_id: str (用户唯一标识)
        :param msg_body: dict (消息体格式，任意选择一种消息类型（文本/图片/语音/视频/文件/图文/自定义消息）填充)
        :param extra: str (自定义字段)
        msg_body:
        文本消息
        {"text": {"content"【required】: str}}
        图片消息
        {"image": {"resource_url"【required】: str}}
        自定义消息
        {"custom": {"content"【required】: str}}
        视频消息
        {"video": {"resource_url"【required】: str(资源链接), "thumb": str(缩略图), "description": str(描述), "title": str(标题)}}
        文件消息
        {"file": {"file_name": "str", "resource_url"【required】: "str"}}
        语音消息
        {
        "voice": {
            "resource_url"【required】: str,
            "type": "AMR"(default AMR, one of AMR PCM WAV OPUS SPEEX MP3),
            "recognition": str(语音识别文本结果)
            }
        }
        图文消息
        {
        "share_link": {
            "description": str(文字描述),
            "destination_url"【required】: str(链接目标地址),
            "cover_url"【required】: str(封面图片地址),
            "title"【required】: str(链接的文字标题)
            }
        }
        :return:
        """
        params = {
            "user_id": user_id,
            "msg_body": msg_body,
            "extra": extra
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/msg/bot-response", params, opts)
        body = self.process_common_request(request)
        return body
        # return BotResponse(**body)

    def create_user_user_attribute(self, user_id: str, user_attribute_user_attribute_value: list, **kwargs):
        """
        给用户添加属性值
        该接口用于给用户添加或修改用户属性，包括预设属性和自定义属性。
        :param user_id:	str (用户id作为用户的唯一识别。)
        :param user_attribute_user_attribute_value: list  (属性列表。重复创建的用户属性会被覆盖。临时属性默认30min有效期。)
        user_attribute_user_attribute_value = [
            {"user_attribute": {"id": "属性id"}, "user_attribute_value": {"name": "属性值"}}, {...}, ...
        ]
        :return:
        """
        params = {
            "user_id": user_id,
            "user_attribute_user_attribute_value": user_attribute_user_attribute_value
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/user/user-attribute/create", params, opts)
        body = self.process_common_request(request)
        return body

    def get_keyword_bot_response(self, user_id: str, msg_body: dict, extra: str="", **kwargs):
        """
        获取关键字机器人回复
        关键字机器人输入用户的文本消息内容，吾来机器人理解并做出响应，返回最合适的关键字机器人回复答复给用户。
        :param user_id: str (用户唯一标识)
        :param msg_body: dict (消息体格式，任意选择一种消息类型（文本/图片/语音/视频/文件/图文/自定义消息）填充)
        :param extra: str (自定义字段)
        msg_body:
        文本消息
        {"text": {"content"【required】: str}}
        图片消息
        {"image": {"resource_url"【required】: str}}
        自定义消息logg
        {"custom": {"content"【required】: str}}
        视频消息
        {"video": {"resource_url"【required】: str(资源链接), "thumb": str(缩略图), "description": str(描述), "title": str(标题)}}
        文件消息
        {"file": {"file_name": "str", "resource_url"【required】: "str"}}
        语音消息
        {
        "voice": {
            "resource_url"【required】: str,
            "type": "AMR"(default AMR, one of AMR PCM WAV OPUS SPEEX MP3),
            "recognition": str(语音识别文本结果)
            }
        }
        图文消息
        {
        "share_link": {
            "description": str(文字描述),
            "destination_url"【required】: str(链接目标地址),
            "cover_url"【required】: str(封面图片地址),
            "title"【required】: str(链接的文字标题)
            }
        }
        :return:
        """
        params = {
            "user_id": user_id,
            "msg_body": msg_body,
            "extra": extra
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/msg/bot-response/keyword", params, opts)
        body = self.process_common_request(request)
        return body

    def get_qa_bot_response(self, user_id: str, msg_body: dict, extra: str="", **kwargs):
        """
        获取问答机器人回复
        问答机器人输入用户的文本消息内容，吾来机器人理解并做出响应，返回最合适的问答机器人回复答复给用户。
        :param user_id: str (用户唯一标识)
        :param msg_body: dict (消息体格式，任意选择一种消息类型（文本/图片/语音/视频/文件/图文/自定义消息）填充)
        :param extra: str (自定义字段)
        msg_body:
        文本消息
        {"text": {"content"【required】: str}}
        图片消息
        {"image": {"resource_url"【required】: str}}
        自定义消息
        {"custom": {"content"【required】: str}}
        视频消息
        {"video": {"resource_url"【required】: str(资源链接), "thumb": str(缩略图), "description": str(描述), "title": str(标题)}}
        文件消息
        {"file": {"file_name": "str", "resource_url"【required】: "str"}}
        语音消息
        {
        "voice": {
            "resource_url"【required】: str,
            "type": "AMR"(default AMR, one of AMR PCM WAV OPUS SPEEX MP3),
            "recognition": str(语音识别文本结果)
            }
        }
        图文消息
        {
        "share_link": {
            "description": str(文字描述),
            "destination_url"【required】: str(链接目标地址),
            "cover_url"【required】: str(封面图片地址),
            "title"【required】: str(链接的文字标题)
            }
        }
        :return:
        """
        params = {
            "user_id": user_id,
            "msg_body": msg_body,
            "extra": extra
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/msg/bot-response/qa", params, opts)
        body = self.process_common_request(request)
        return body

    def get_task_bot_response(self, user_id: str, msg_body: dict, extra: str="", **kwargs):
        """
        获取任务机器人回复
        任务机器人输入用户的文本消息内容，吾来机器人理解并做出响应，返回最合适的任务机器人回复答复给用户。
        :param user_id: str (用户唯一标识)
        :param msg_body: dict (消息体格式，任意选择一种消息类型（文本/图片/语音/视频/文件/图文/自定义消息）填充)
        :param extra: str (自定义字段)
        msg_body:
        文本消息
        {"text": {"content"【required】: str}}
        图片消息
        {"image": {"resource_url"【required】: str}}
        自定义消息
        {"custom": {"content"【required】: str}}
        视频消息
        {"video": {"resource_url"【required】: str(资源链接), "thumb": str(缩略图), "description": str(描述), "title": str(标题)}}
        文件消息
        {"file": {"file_name": "str", "resource_url"【required】: "str"}}
        语音消息
        {
        "voice": {
            "resource_url"【required】: str,
            "type": "AMR"(default AMR, one of AMR PCM WAV OPUS SPEEX MP3),
            "recognition": str(语音识别文本结果)
            }
        }
        图文消息
        {
        "share_link": {
            "description": str(文字描述),
            "destination_url"【required】: str(链接目标地址),
            "cover_url"【required】: str(封面图片地址),
            "title"【required】: str(链接的文字标题)
            }
        }
        :return:
        """
        params = {
            "user_id": user_id,
            "msg_body": msg_body,
            "extra": extra
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/msg/bot-response/task", params, opts)
        body = self.process_common_request(request)
        return body

    def sync_message(self, user_id: str, msg_body: dict, msg_ts: str, extra: str="", **kwargs):
        """
        同步发给用户的消息
        如果机器人接入第三方消息渠道，需要把发给用户的所有消息同步给吾来，这样才可以在吾来查看到全部消息记录。
        :param user_id: str (用户唯一标识)
        :param msg_body: dict (消息体格式，任意选择一种消息类型（文本/图片/语音/视频/文件/图文/自定义消息）填充)
        :param msg_ts: str (消息毫秒级时间戳)
        :param extra: str (自定义字段)
        msg_body:
        文本消息
        {"text": {"content"【required】: str}}
        图片消息
        {"image": {"resource_url"【required】: str}}
        自定义消息
        {"custom": {"content"【required】: str}}
        视频消息
        {"video": {"resource_url"【required】: str(资源链接), "thumb": str(缩略图), "description": str(描述), "title": str(标题)}}
        文件消息
        {"file": {"file_name": "str", "resource_url"【required】: "str"}}
        语音消息
        {
        "voice": {
            "resource_url"【required】: str,
            "type": "AMR"(default AMR, one of AMR PCM WAV OPUS SPEEX MP3),
            "recognition": str(语音识别文本结果)
            }
        }
        图文消息
        {
        "share_link": {
            "description": str(文字描述),
            "destination_url"【required】: str(链接目标地址),
            "cover_url"【required】: str(封面图片地址),
            "title"【required】: str(链接的文字标题)
            }
        }
        :return:
        """
        params = {
            "user_id": user_id,
            "msg_body": msg_body,
            "msg_ts": msg_ts,
            "extra": extra
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/msg/sync", params, opts)
        body = self.process_common_request(request)
        return body

    def receive_message(self, user_id: str, msg_body: dict, third_msg_id: str="", extra: str="", **kwargs):
        """
        接收用户发的消息
        如果机器人接入第三方消息渠道，需要把用户发的所有消息同步给吾来，可以实现机器人全自动交互场景（参考异步基础对话、异步定制对话）。
        :param user_id: str (用户唯一标识)
        :param msg_body: dict (消息体格式，任意选择一种消息类型（文本/图片/语音/视频/文件/图文/自定义消息）填充)
        :param third_msg_id: str  (接入方唯一msg_id，保证1分钟内的幂等性)
        :param extra: str (自定义字段)
        msg_body:
        文本消息
        {"text": {"content"【required】: str}}
        图片消息
        {"image": {"resource_url"【required】: str}}
        自定义消息
        {"custom": {"content"【required】: str}}
        视频消息
        {"video": {"resource_url"【required】: str(资源链接), "thumb": str(缩略图), "description": str(描述), "title": str(标题)}}
        文件消息
        {"file": {"file_name": "str", "resource_url"【required】: "str"}}
        语音消息
        {
        "voice": {
            "resource_url"【required】: str,
            "type": "AMR"(default AMR, one of AMR PCM WAV OPUS SPEEX MP3),
            "recognition": str(语音识别文本结果)
            }
        }
        图文消息
        {
        "share_link": {
            "description": str(文字描述),
            "destination_url"【required】: str(链接目标地址),
            "cover_url"【required】: str(封面图片地址),
            "title"【required】: str(链接的文字标题)
            }
        }
        :return:
        """
        params = {
            "user_id": user_id,
            "msg_body": msg_body,
            "third_msg_id": third_msg_id,
            "extra": extra
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/msg/receive", params, opts)
        body = self.process_common_request(request)
        return body

    def get_message_history(self, user_id: str, num: int, direction: str="BACKWARD", msg_id: str="", **kwargs):
        """
        查询历史消息
        获取与指定用户发生的历史对话消息。
        :param user_id: str (用户唯一标识)
        :param num: int  (一次获取消息的数目 -> [1, 50])
        :param direction: str (翻页方向)
            BACKWARD: 向旧的消息翻页，查询比传入msg_id更小的消息
            FORWARD: 先新的消息翻页，查询比传入msg_id更大的消息
        :param msg_id: str (从这个msg_id开始查询（结果包含此条消息）；为空时查询最新的消息)
        :return:
        """
        params = {
            "user_id": user_id,
            "num": num,
            "direction": direction,
            "msg_id": msg_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/msg/history", params, opts)
        body = self.process_common_request(request)
        return body
