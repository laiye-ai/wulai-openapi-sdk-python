import time
import uuid
import hashlib
import logging

from wulaisdk.http import BaseRequest
from wulaisdk import http_codes
from wulaisdk.request import CommonRequest
from wulaisdk.exceptions import ServerException, ClientException, ERR_INFO

from requests.exceptions import ConnectionError, ConnectTimeout


DEBUG = False

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.addHandler(handler)


class WulaiClient:
    def __init__(self, pubkey: str, secret: str, endpoint: str="https://openapi.wul.ai",
                 api_version: str="v2", debug: bool=False, pool=None, pool_connections: int=10, pool_maxsize: int=10,
                 max_retries: int=3):
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

    def logger_level_init(self):
        global logger
        if DEBUG:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.ERROR)

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
            raise exception
        logger.debug("Response received. Action: {}. Response-body: {}".format(request.action, body))
        return body

    def create_user(self, user_id: str, avatar_url: str="", nickname: str=""):
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
        opts = {
            "method": "POST",
            "retry": 2
        }

        request = CommonRequest("/user/create", params, opts)
        body = self.process_common_request(request)
        return body

    def get_bot_response(self, user_id: str, msg_body: dict, extra: str=""):
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
        事件消息
        todo
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
        opts = {
            "method": "POST",
            "retry": 2
        }

        request = CommonRequest("/msg/bot-response", params, opts)
        body = self.process_common_request(request)
        return body

    def create_user_user_attribute(self, user_id: str, user_attribute_user_attribute_value: list):
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
        opts = {
            "method": "POST",
            "retry": 2
        }

        request = CommonRequest("/user/user-attribute/create", params, opts)
        body = self.process_common_request(request)
        return body
