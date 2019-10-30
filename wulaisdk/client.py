import time
import uuid
import hashlib
import logging

from wulaisdk.http import BaseRequest
from wulaisdk import http_codes
from wulaisdk.request import CommonRequest
from wulaisdk.exceptions import ServerException, ClientException, ERR_INFO

from requests.exceptions import ConnectionError, ConnectTimeout
from wulaisdk.response.bot_response import BotResponse
from wulaisdk.response.keyword_bot_response import KeywordBotResponse
from wulaisdk.response.qa_bot_response import QABotResponse
from wulaisdk.response.task_bot_response import TaskBotResponse
from wulaisdk.response.sync_message import SyncMessage
from wulaisdk.response.receive_message import ReceiveMessage
from wulaisdk.response.history_message import HistoryMessage
from wulaisdk.response.knowledge import KnowledgeCreate, KnowledgeUpdate, KnowledgeItems, KnowledgeTags
from wulaisdk.response.similar_question import SimilarQuestionCreate, SimilarQuestions, SimilarQuestionUpdate
from wulaisdk.response.user_attribute_group import CreateUserAttributeGroup, UpdateUserAttributeGroup,\
    UpdateUserAttributeGroupItems, CreateUserAttributeGroupAnswer, UpdateUserAttributeGroupAnswer,\
    UserAttributeGroupAnswers, UserUserAttribute, UserAttributes


DEBUG = False

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(process)d %(thread)d %(levelname)s %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
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

    def create_user_attribute(self, user_attribute_user_attribute_value: list, user_id: str, **kwargs):
        """
        给用户添加属性值
        该接口用于给用户添加或修改用户属性，包括系统属性和临时属性。
        :param user_attribute_user_attribute_value: list (属性列表。重复创建的用户属性会被覆盖。临时属性默认30min有效期。)
        :param user_id:	str (用户id作为用户的唯一识别。)[ 1 .. 128 ] characters
        user_attribute_user_attribute_value:
        [
            {
                "user_attribute"【required】(用户属性): {"id": str},
                "user_attribute_value"【required】(用户属性值): {"name": str}
            }
        ]
        :return:
        """
        params = {
            "user_attribute_user_attribute_value": user_attribute_user_attribute_value,
            "user_id": user_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/user/user-attribute/create", params, opts)
        body = self.process_common_request(request)
        return body

    def user_user_attribute(self, user_id: str, **kwargs):
        """
        查询用户的属性值
        查询一个用户的所有属性和属性值。
        :param user_id:	str (用户id作为用户的唯一识别。)[ 1 .. 128 ] characters
        :return:
        """
        params = {
            "user_id": user_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/user/user-attribute/pair/list", params, opts)
        body = self.process_common_request(request)
        return UserUserAttribute.from_dict(body)

    def user_attributes(self, page: int, page_size: int, filter: dict=None, **kwargs):
        """
        获取用户属性列表
        该接口用于查询符合过滤条件的用户属性及其属性值。
        如果没有过滤条件，则返回所有用户属性及其属性值。
        当一个用户属性关联多个属性值时，会返回的user_attribute_user_attribute_values中有多组。
        比如：用户属性“性别”有属性值“男”，“女”。则接口返回的user_attribute_user_attribute_values有两组。
        :param page:	    int (页码，代表查看第几页的数据，从1开始)
        :param page_size:	int (每页的属性组数量)
        :param filter:	    dict (过滤条件。结构体中字段，如果填写，代表需要过滤；反之不过滤。)
        filter:
        {
            "use_in_user_attribute_group"【required】: bool (是否可以作为属性组属性)
        }
        :return:
        """
        params = {
            "page": page,
            "page_size": page_size,
            "filter": filter,
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/user-attribute/list", params, opts)
        body = self.process_common_request(request)
        return UserAttributes.from_dict(body)

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
        return BotResponse.from_dict(body)

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
        return KeywordBotResponse.from_dict(body)

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
        return QABotResponse.from_dict(body)

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
        return TaskBotResponse.from_dict(body)

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
        return SyncMessage.from_dict(body)

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
        return ReceiveMessage.from_dict(body)

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
        return HistoryMessage.from_dict(body)

    # 知识点类
    def create_knowledge(self, knowledge_tag_knowledge: dict, **kwargs):
        """
        创建知识点
        该接口可创建知识点，并同时定义知识点的标准问、是否使用属性组、生效状态、以及知识点所属分类。
        注:只有当一个知识点分类已经在吾来平台中创建后，才可在该接口中传入其id。如果知识点分类id尚未在系统中创建，则无法成功创建知识点
        :param knowledge_tag_knowledge: dict (知识点)
        knowledge_tag_knowledge:
        {
            "knowledge"【required】: {
                "status"【required】: bool(知识点状态),
                "standard_question"【required】: str(知识点标题),
                "respond_all"【required】: bool(发送全部回复),
                "id": str(知识点id，创建时可不传该参数或传None),
                "maintained_by_user_attribute_group"【required】: bool,
            },
            "knowledge_tag_id"【required】: str(知识点分类id)
        }
        :return:
        """
        params = {
            "knowledge_tag_knowledge": knowledge_tag_knowledge,
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/qa/knowledge-tag-knowledge/create", params, opts)
        body = self.process_common_request(request)
        return KnowledgeCreate.from_dict(body)

    def update_knowledge(self, knowledge: dict, **kwargs):
        """
        更新知识点
        该接口可更新知识点相关信息，具体内容包含知识点的标准问、是否使用属性组、生效状态、以及知识点所属分类。
        :param knowledge: dict (知识点详情)
        "knowledge":
        {
            "status"【required】: bool(知识点状态),
            "standard_question": str(知识点标题),
            "respond_all"【required】: bool(发送全部回复),
            "id"【required】: str(知识点id),
            "maintained_by_user_attribute_group"【required】: bool,
        }
        :return:
        """
        params = {
            "knowledge": knowledge,
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/qa/knowledge/update", params, opts)
        body = self.process_common_request(request)
        return KnowledgeUpdate.from_dict(body)

    def knowledge_items(self, page: int, page_size: int, **kwargs):
        """
        查询知识点列表
        该接口可返回知识点相关信息，具体内容包含知识点所在分类、知识点标准问以及相似问。
        返回的知识点范围为：调用时使用的开放平台Pubkey所属的项目(APP)中的所有知识点。
        :param page: int (页码，代表查看第几页的数据)
        :param page_size: int (每页的知识点数量)
        :return:
        """
        params = {
            "page": page,
            "page_size": page_size,
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/qa/knowledge-items/list", params, opts)
        body = self.process_common_request(request)
        return KnowledgeItems.from_dict(body)

    def knowledge_tags(self, page: int, page_size: int, parent_k_tag_id: str=None, **kwargs):
        """
        查询知识点分类列表
        该接口可返回知识点分类以及各分类所在的父类。返回的知识点分类范围为：调用时使用的开放平台Pubkey所属的项目(APP)中的所有知识点分类。
        :param page: int (页码，代表查看第几页的数据)
        :param page_size: int (每页的知识点分类数量)
        :param parent_k_tag_id: str (父节点分类id，如果不传值，代表获取根节点下的知识点分类)
        :return:
        """
        params = {
            "page": page,
            "page_size": page_size,
            "parent_k_tag_id": parent_k_tag_id,
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/qa/knowledge-tags/list", params, opts)
        body = self.process_common_request(request)
        return KnowledgeTags.from_dict(body)

    def create_similar_question(self, similar_question: dict, **kwargs):
        """
        创建相似问
        该接口可创建相似问，具体内容包括相似问所关联的知识点、和相似问的内容。
        注:只有当知识点id已经在吾来平台中创建后，才可通过该接口创建相似问。如果知识点id尚未在系统中创建，则无法成功创建相似问。
        :param similar_question: dict (相似问详情)
        {
            "knowledge_id"【required】: str(知识点id),
            "question"【required】: str(相似问),
            "id": str(相似问id),
        }
        :return:
        """
        params = {
            "similar_question": similar_question,
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/qa/similar-question/create", params, opts)
        body = self.process_common_request(request)
        return SimilarQuestionCreate.from_dict(body)

    def update_similar_question(self, similar_question: dict, **kwargs):
        """
        更新相似问
        该接口可创建相似问，具体内容包括相似问所关联的知识点、和相似问的内容。
        注:只有当知识点id已经在吾来平台中创建后，才可通过该接口创建相似问。如果知识点id尚未在系统中创建，则无法成功创建相似问。
        :param similar_question: dict (相似问详情)
        {
            "knowledge_id"【required】: str(知识点id),
            "question": str(相似问，相似问的值不可为空字符串),
            "id"【required】: str(相似问id),
        }
        :return:
        """
        params = {
            "similar_question": similar_question,
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/qa/similar-question/update", params, opts)
        body = self.process_common_request(request)
        return SimilarQuestionUpdate.from_dict(body)

    def delete_similar_question(self, similar_id: str, **kwargs):
        """
        删除相似问
        该接口可删除相似问。
        :param similar_id: str (相似问id)
        :return:
        """
        params = {
            "id": similar_id,
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/qa/similar-question/delete", params, opts)
        body = self.process_common_request(request)
        return body

    def similar_questions(self, page: int, page_size: int, knowledge_id: str=None, similar_question_id: str=None, **kwargs):
        """
        查询相似问列表
        该接口可返回相似问的相关信息，包括相似问所关联的知识点、和相似问的内容。 调用方可选择根据知识点查询（在请求参数中传入知识点id）、
        根据相似问查询（在请求参数中传入相似问id）、或者查询所有知识点问题（在请求参数中不传入任何filter）。
        :param page: int (页码，代表查看第几页的数据，从1开始)
        :param page_size: int (每页的属性组数量)
        :param knowledge_id: str (知识点id)
        :param similar_question_id: str (相似问id)
        :return:
        """
        params = {
            "page": page,
            "page_size": page_size,
            "knowledge_id": knowledge_id,
            "similar_question_id": similar_question_id,
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/qa/similar-question/list", params, opts)
        body = self.process_common_request(request)
        return SimilarQuestions.from_dict(body)

    def create_user_attribute_group_items(self, user_attribute_group_item: dict, **kwargs):
        """
        创建属性组
        该接口用于创建属性组，具体内容包括属性组名称，及构成该属性组的用户属性和属性值。
        :param user_attribute_group_item: 用户属性组及属性
        {
            "user_attribute_user_attribute_value"【required】: list(属性。
                我们用A代表此处传入的属性列表。
                调用获取用户属性列表接口，请求值传filter.use_in_user_attribute_group=true，获取到可以作为属性组的属性列表B。

                要求A中每个元素都要在B中存在，如不存在接口将报错。
                不要求B中每个属性都在A中存在，如不存在代表通配所有属性值。),
            "user_attribute_group"【required】: dict(用户属性组详情)
        }
        user_attribute_user_attribute_value:
        [
            {
                "user_attribute"【required】: dict(用户属性) {"id": str(属性id)},
                "user_attribute_value"【required】: dict（用户属性值）{"name": str(属性值)}
            }
        ]
        user_attribute_group:
        {
            "name"【required】: str(属性组名称)
        }
        :param kwargs:
        :return:
        """

        params = {
            "user_attribute_group_item": user_attribute_group_item,
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/qa/user-attribute-group-items/create", params, opts)
        body = self.process_common_request(request)
        return CreateUserAttributeGroup.from_dict(body)

    def update_user_attribute_group_items(self, user_attribute_group_item: dict, **kwargs):
        """
        更新属性组
        该接口用于更新属性组，具体内容包括属性组名称，及构成该属性组的用户属性和属性值。
        :param user_attribute_group_item: 用户属性组及属性
        {
            "user_attribute_user_attribute_value": list(属性。
                如果不传这个字段，代表不修改；如果填写，则把该属性组的旧属性全部删除，重新添加。
                我们用A代表此处传入的属性列表。
                调用获取用户属性列表接口，请求值传filter.use_in_user_attribute_group=true，获取到可以作为属性组的属性列表B。

                要求A中每个元素都要在B中存在，如不存在接口将报错。
                不要求B中每个属性都在A中存在，如不存在代表通配所有属性值。),
            "user_attribute_group"【required】: dict(用户属性组详情)
        }
        user_attribute_user_attribute_value:
        [
            {
                "user_attribute"【required】: dict(用户属性) {"id": str(属性id)},
                "user_attribute_value"【required】: dict（用户属性值）{"name": str(属性值)}
            }
        ]
        user_attribute_group:
        {
            "id"【required】: str(属性组id)
            "name": str(属性组名称。如果不传这个字段，代表不修改)
        }
        :param kwargs:
        :return:
        """

        params = {
            "user_attribute_group_item": user_attribute_group_item,
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/qa/user-attribute-group-items/update", params, opts)
        body = self.process_common_request(request)
        return UpdateUserAttributeGroup.from_dict(body)

    def user_attribute_group_items(self, page: int, page_size: int, **kwargs):
        """
        查询属性组及属性列表
        该接口可返回属性组相关信息，包括属性组名称、属性组内所包含的属性和属性值。
        返回的范围为：调用时使用的开放平台Pubkey所属的项目(APP)中的所有属性组。
        :param page: int(页码，代表查看第几页的数据，从1开始)
        :param page_size: int(用户属性组及属性)
        :param kwargs:
        :return:
        """

        params = {
            "page": page,
            "page_size": page_size
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/qa/user-attribute-group-items/list", params, opts)
        body = self.process_common_request(request)
        return UpdateUserAttributeGroupItems.from_dict(body)

    def create_user_attribute_group_answer(self, user_attribute_group_answer: dict, **kwargs):
        """
        创建属性组回复
        该接口可创建属性组回复，具体内容包括属性组回复所关联的知识点、和属性组回复的消息内容。
        注:只有当知识点id已经在吾来平台中创建后，才可通过该接口创建属性组回复。如果知识点id尚未在系统中创建，则无法成功创建属性组回复
        :param user_attribute_group_answer: dict(属性组)
        {
            "answer"【required】: dict(回复)
            "user_attribute_group_id"【required】: str(属性组id)
        }
        answer:
        {
            "knowledge_id"【required】: str(知识点id),
            "msg_body"【required】: dict(消息体格式，任意选择一种消息类型（文本 / 图片 / 语音 / 视频 / 文件 / 图文 / 自定义消息）填充),
            "id": str(回复id，创建回复时不需要填写，更新回复时需要填写)
        }
        :param kwargs:
        :return:
        """

        params = {
            "user_attribute_group_answer": user_attribute_group_answer
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/qa/user-attribute-group-answer/create", params, opts)
        body = self.process_common_request(request)
        return CreateUserAttributeGroupAnswer.from_dict(body)

    def update_user_attribute_group_answer(self, user_attribute_group_answer: dict, **kwargs):
        """
        更新属性组回复
        该接口可更新属性组回复，具体内容包括属性组回复所关联的知识点、和属性组回复的消息内容。
        :param user_attribute_group_answer: dict(属性组)
        {
            "answer"【required】: dict(回复)
            "user_attribute_group_id"【required】: str(属性组id)
        }
        answer:
        {
            "knowledge_id"【required】: str(知识点id),
            "msg_body"【required】: dict(消息体格式，任意选择一种消息类型（文本 / 图片 / 语音 / 视频 / 文件 / 图文 / 自定义消息）填充),
            "id"【required】: str(回复id，创建回复时不需要填写，更新回复时需要填写)
        }
        :param kwargs:
        :return:
        """

        params = {
            "user_attribute_group_answer": user_attribute_group_answer
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/qa/user-attribute-group-answer/update", params, opts)
        body = self.process_common_request(request)
        return UpdateUserAttributeGroupAnswer.from_dict(body)

    def user_attribute_group_answers(self, page: int, page_size: int, kn_filter: dict=None, **kwargs):
        """
        查询属性组回复列表
        该接口可返回属性组回复相关信息，包括属性组回复所关联的知识点、和属性组回复的消息内容。
        调用方可选择根据知识点查询（在请求参数中传入知识点id）、根据属性组查询（在请求参数中传入属性组id）、
        或者查询所有属性组回复（在请求参数中不传入任何filter）。
        :param page: int(页码，代表查看第几页的数据，从1开始)
        :param page_size: int(用户属性组及属性)
        :param kn_filter: dict(过滤条件。结构体中字段，如果填写，代表需要过滤；反之不过滤。)
        {
            "knowledge_id": str(知识点id，如不填写，返回所有知识点),
            "user_attribute_group_id": str(属性组id，如不填写，返回所有属性组)
        }
        :param kwargs:
        :return:
        """
        params = {
            "page": page,
            "page_size": page_size,
            "filter": kn_filter,
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/qa/user-attribute-group-answers/list", params, opts)
        body = self.process_common_request(request)
        return UserAttributeGroupAnswers.from_dict(body)

    def delete_user_attribute_group_answer(self, uaga_id: dict, **kwargs):
        """
        删除属性组回复
        该接口用于删除一条属性组的回复。
        :param uaga_id: int(属性组回复id)
        :param kwargs:
        :return:
        """
        params = {
            "id": uaga_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/qa/user-attribute-group-answer/delete", params, opts)
        body = self.process_common_request(request)
        return body
