import time
import uuid
import hashlib
import logging
import sys
import requests

from wulaisdk.http import BaseRequest
from wulaisdk import http_codes
from wulaisdk.request import CommonRequest
from wulaisdk.exceptions import ServerException, ClientException, ERR_INFO

from requests.exceptions import ConnectionError, ConnectTimeout

from wulaisdk.response.category_user import UserUserAttribute, UserAttributes, GetUser
from wulaisdk.response.category_talk import BotResponse, KeywordBotResponse, QABotResponse, TaskBotResponse,\
    SyncMessage, ReceiveMessage, HistoryMessage, SendMessage, GetUserSuggestion
from wulaisdk.response.category_knowledge import KnowledgeCreate, KnowledgeUpdate, KnowledgeItems, KnowledgeTags,\
    SimilarQuestionCreate, SimilarQuestions, SimilarQuestionUpdate,CreateUserAttributeGroup, UpdateUserAttributeGroup,\
    UpdateUserAttributeGroupItems, CreateUserAttributeGroupAnswer, UpdateUserAttributeGroupAnswer,\
    UserAttributeGroupAnswers, KnowledgeTagCreate, KnowledgeTagUpdate, KnowledgeBatchCreate
from wulaisdk.response.category_stats import StatsQASatisfactionKnowledgeDaily, StatsQARecallDaily,\
    StatasQARecallDailyKnowledges
from wulaisdk.response.category_dictionary import DictionaryEntities, DictionaryTerms, DictionaryTerm, \
    DictionaryEntity, CreateEnumEntity, CreateEnumEntityValue, CreateIntentEntity, CreateIntentEntityValue
from wulaisdk.response.category_nlp import EntityExtract, Tokenize, MiningUpload, MiningExecute, MiningResult
from wulaisdk.response.category_task import Scenes, CreateScene, UpdateScene, Intents, CreateIntent, UpdateIntent,\
    IntentTriggers, CreateIntentTrigger, UpdateIntentTrigger, Slots, CreateSlot, UpdateSlot, SlotDataSource, GetSlot,\
    CreateSlotDataSource, GetInformBlock, CreateInformBlock, UpdateInformBlock, GetRequestBlock,\
    CreateRequestBlock, UpdateRequestBlock, CreateResponse, UpdateResponse, GetEndBlock, CreateEndBlock,\
    UpdateEndBlock, CreateBlockRelation, IntentTriggerLearning, UpdateIntentStatus, Blocks
from wulaisdk.response.category_config import UpdateConfig


DEBUG = False
SDK_VERSION = "1.1.8"

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
        if not self.api_version.startswith("v"):
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

    def add_user_agent(self, request):
        """
        add User-Agent for request
        :param request:
        :return:
        """
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        requests_version = requests.__version__
        request.add_headers(
            "User-Agent",
            f"wulai-openapi-sdk-python/{self.api_version}-{SDK_VERSION} python/{py_version} requests/{requests_version}"
        )

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
        self.add_user_agent(request)
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

    # 用户类
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
        （该接口不小心创建重复，和下述create_user_user_attribute的功能没有区别）
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

    def create_user_user_attribute(self, user_id: str, user_attribute_user_attribute_value: list, **kwargs):
        """
        给用户添加属性值
        该接口用于给用户添加或修改用户属性，包括预设属性和自定义属性。
        :param user_id:	str (用户id作为用户的唯一识别。)
        :param user_attribute_user_attribute_value: list  (属性列表。重复创建的用户属性会被覆盖。临时属性默认30min有效期。)
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
            "user_id": user_id,
            "user_attribute_user_attribute_value": user_attribute_user_attribute_value
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

    def get_user(self, user_id: str, **kwargs):
        """
        查询用户信息
        获取一个用户的详细信息。
        :param user_id:	str (用户id)[ 1 .. 128 ] characters

        :return:
        """
        params = {
            "user_id": user_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/user/get", params, opts)
        body = self.process_common_request(request)
        return GetUser.from_dict(body)

    def update_user(self, user_id: str, avatar_url: str=None, nickname: str=None, **kwargs):
        """
        更新用户信息
        更新用户昵称和头像地址。
        :param user_id:	str (用户id)[ 1 .. 128 ] characters
        :param avatar_url: 	str (用户头像地址。用户头像会展示在吾来SaaS的用户列表、消息记录等任何展示用户信息的地方) <= 512 characters
        :param nickname: str (用户昵称) <= 128 characters
        :return:
        """
        params = {
            "user_id": user_id,
            "avatar_url": avatar_url,
            "nickname": nickname
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/user/update", params, opts)
        body = self.process_common_request(request)
        return body

    # 对话类
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
        卡片消息
        {
        "share_link": {
            "description": str(文字描述),
            "destination_url"【required】: str(链接目标地址),
            "cover_url"【required】: str(封面图片地址),
            "title"【required】: str(链接的文字标题)
            }
        }
        图文消息
        {"rich_text": {"resource_url"【required】: str}}
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
        卡片消息
        {
        "share_link": {
            "description": str(文字描述),
            "destination_url"【required】: str(链接目标地址),
            "cover_url"【required】: str(封面图片地址),
            "title"【required】: str(链接的文字标题)
            }
        }
        图文消息
        {"rich_text": {"resource_url"【required】: str}}
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
        卡片消息
        {
        "share_link": {
            "description": str(文字描述),
            "destination_url"【required】: str(链接目标地址),
            "cover_url"【required】: str(封面图片地址),
            "title"【required】: str(链接的文字标题)
            }
        }
        图文消息
        {"rich_text": {"resource_url"【required】: str}}
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
        卡片消息
        {
        "share_link": {
            "description": str(文字描述),
            "destination_url"【required】: str(链接目标地址),
            "cover_url"【required】: str(封面图片地址),
            "title"【required】: str(链接的文字标题)
            }
        }
        图文消息
        {"rich_text": {"resource_url"【required】: str}}
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

    def sync_message(self, user_id: str, msg_body: dict, msg_ts: str, extra: str="",
                     answer_id: int=None, bot: dict=None, **kwargs):
        """
        同步发给用户的消息
        如果机器人接入第三方消息渠道，需要把发给用户的所有消息同步给吾来，这样才可以在吾来查看到全部消息记录。
        如果需要使用满意度评价接口，则需要在调用本接口时传入机器人信息(bot)。
        :param user_id: str (用户唯一标识)
        :param msg_body: dict (消息体格式，任意选择一种消息类型（文本/图片/语音/视频/文件/图文/自定义消息）填充)
        :param msg_ts: str (消息毫秒级时间戳)
        :param extra: str (自定义字段)
        :param answer_id: int (答案id)
        :param bot: dict (机器人回复)
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
        卡片消息
        {
        "share_link": {
            "description": str(文字描述),
            "destination_url"【required】: str(链接目标地址),
            "cover_url"【required】: str(封面图片地址),
            "title"【required】: str(链接的文字标题)
            }
        }
        图文消息
        {"rich_text": {"resource_url"【required】: str}}

        bot:
        问答机器人
        {
        "qa": {
            "knowledge_id": int (知识点id),
            "standard_question": str (标准问 <=100 characters),
            "question": str (命中的相似问 <=1024 characters),
            "is_none_intention": str (是否为无意图知识点),
            }
        }
        闲聊机器人
        {
        "chitchat": {
            "corpus": str (闲聊机器人类型:
                CHITCHAT_CORPUS_OPEN_DOMAIN: 开放闲聊
                CHITCHAT_CORPUS_CUSTOM: 自定义闲聊)
            }
        }
        任务机器人
        {
        "task": {
            "block_type": str (对话单元类型:
                BLOCK_TYPE_MESSAGE: 消息单元
                BLOCK_TYPE_ASK: 询问单元
                BLOCK_TYPE_HIDE: 隐藏单元
                BLOCK_TYPE_LINK: 跳转单元
                BLOCK_TYPE_ADVANCE_INTERFACE: 高级接口
                BLOCK_TYPE_INTERFACE: 接口单元
                BLOCK_TYPE_CALCULATE: 运算单元
                BLOCK_TYPE_COLLECT: 收集单元),
            "block_id": int (任务型机器人对话单元id),
            "task_id": int (任务id),
            "block_name": str (任务机器人对话单元名),
            "entities": list (抽取的实体列表),
            "task_name": str (任务机器人任务名),
            "robot_id": int (机器人id)
            }
        }
        entities:
        [
            {
                "idx_end": int (实体值原始片段在query中的结束位置),
                "name": str (实体名称),
                "idx_start": int (实体值原始片段在query中的起始位置),
                "value": str (实体值),
                "seg_value": str (实体值的原始片段),
                "type": str (实体类型枚举:
                    NTITY_TYPE_SYS: 系统实体
                    ENTITY_TYPE_UDEFINE: 用户自定义实体
                    ENTITY_TYPE_CONTENT: 自由文本实体
                    ENTITY_TYPE_REGEX: 正则实体
                    ENTITY_TYPE_CITE: 引用实体
                    ENTITY_TYPE_WEBHOOK: webhook实体
                    ENTITY_TYPE_USERACT: user_act),
                "desc": str (实体别名),
            }
        ]
        关键字机器人
        {
        "keyword": {
            "keyword_id": int (关键字id),
            "keyword": str (命中的关键字 <=128 characters),
            }
        }


        :return:
        """
        params = {
            "user_id": user_id,
            "msg_body": msg_body,
            "msg_ts": msg_ts,
            "extra": extra,
            "bot": bot,
            "answer_id": answer_id
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
        卡片消息
        {
        "share_link": {
            "description": str(文字描述),
            "destination_url"【required】: str(链接目标地址),
            "cover_url"【required】: str(封面图片地址),
            "title"【required】: str(链接的文字标题)
            }
        }
        图文消息
        {"rich_text": {"resource_url"【required】: str}}
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

    def send_message(self, user_id: str, msg_body: dict, quick_reply: list=None,
                     similar_response: list=None, extra: str=None, **kwargs):
        """
        给用户发消息
        :param user_id: str(用户唯一标识) [ 1 .. 128 ] characters
        :param msg_body: dict(消息体格式，任意选择一种消息类型（文本 / 图片 / 语音 / 视频 / 文件 / 图文 / 自定义消息）填充)
        :param quick_reply: list(快捷回复) <= 5 items
        :param similar_response: list(推荐知识点) <= 5 items
        :param extra: str(自定义字段) <= 1024 characters
        :param kwargs:
        :return:
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
        卡片消息
        {
        "share_link": {
            "description": str(文字描述),
            "destination_url"【required】: str(链接目标地址),
            "cover_url"【required】: str(封面图片地址),
            "title"【required】: str(链接的文字标题)
            }
        }
        图文消息
        {"rich_text": {"resource_url"【required】: str}}
        similar_response:
        [
            {
                "source": str(回复的来源)
                    DEFAULT_ANSWER_SOURCE: 机器人回复兜底内容
                    KEYWORD_BOT: 关键字机器人
                    TASK_BOT: 任务机器人
                    QA_BOT: 问答机器人
                    CHITCHAT_BOT: 闲聊机器人,
                "detail": dict
            }
        ]
        detail:
        问答机器人
        {
        "qa": {
            "knowledge_id": int (知识点id),
            "standard_question": str (标准问 <=100 characters),
            "question": str (命中的相似问 <=1024 characters),
            "is_none_intention": str (是否为无意图知识点),
            }
        }
        闲聊机器人
        {
        "chitchat": {
            "corpus": str (闲聊机器人类型:
                CHITCHAT_CORPUS_OPEN_DOMAIN: 开放闲聊
                CHITCHAT_CORPUS_CUSTOM: 自定义闲聊)
            }
        }
        任务机器人
        {
        "task": {
            "block_type": str (对话单元类型:
                BLOCK_TYPE_MESSAGE: 消息单元
                BLOCK_TYPE_ASK: 询问单元
                BLOCK_TYPE_HIDE: 隐藏单元
                BLOCK_TYPE_LINK: 跳转单元
                BLOCK_TYPE_ADVANCE_INTERFACE: 高级接口
                BLOCK_TYPE_INTERFACE: 接口单元
                BLOCK_TYPE_CALCULATE: 运算单元
                BLOCK_TYPE_COLLECT: 收集单元),
            "block_id": int (任务型机器人对话单元id),
            "task_id": int (任务id),
            "block_name": str (任务机器人对话单元名),
            "entities": list (抽取的实体列表),
            "task_name": str (任务机器人任务名),
            "robot_id": int (机器人id)
            }
        }
        entities:
        [
            {
                "idx_end": int (实体值原始片段在query中的结束位置),
                "name": str (实体名称),
                "idx_start": int (实体值原始片段在query中的起始位置),
                "value": str (实体值),
                "seg_value": str (实体值的原始片段),
                "type": str (实体类型枚举:
                    NTITY_TYPE_SYS: 系统实体
                    ENTITY_TYPE_UDEFINE: 用户自定义实体
                    ENTITY_TYPE_CONTENT: 自由文本实体
                    ENTITY_TYPE_REGEX: 正则实体
                    ENTITY_TYPE_CITE: 引用实体
                    ENTITY_TYPE_WEBHOOK: webhook实体
                    ENTITY_TYPE_USERACT: user_act),
                "desc": str (实体别名),
            }
        ]
        关键字机器人
        {
        "keyword": {
            "keyword_id": int (关键字id),
            "keyword": str (命中的关键字 <=128 characters),
            }
        }
        """
        params = {
            "user_id": user_id,
            "msg_body": msg_body,
            "similar_response": similar_response,
            "quick_reply": quick_reply,
            "extra": extra
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/msg/send", params, opts)
        body = self.process_common_request(request)
        return SendMessage.from_dict(body)

    def get_user_suggestion(self, user_id: str, query: str, **kwargs):
        """
        获取用户输入联想
        在用户输入时提供相似知识点联想，减少用户的输入成本。
        :param user_id: str (用户Id) [ 1 .. 128 ] characters
        :param query: str (用户输入) [ 1 .. 128 ] characters
        :param kwargs:
        :return:
        """
        params = {
            "user_id": user_id,
            "query": query
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/msg/user-suggestion/get", params, opts)
        body = self.process_common_request(request)
        return GetUserSuggestion.from_dict(body)

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

    def delete_knowledge(self, knowledge_id: int, **kwargs):
        """
        删除知识点
        该接口可删除一个知识点，如果一个知识点关联了相似问、或未删除的属性组回复，则一并删除
        :param knowledge_id: int (知识点id) >= 1
        :return:
        """
        params = {
            "id": knowledge_id,
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/qa/knowledge/delete", params, opts)
        body = self.process_common_request(request)
        return body

    def knowledge_items(self, page: int, page_size: int, knowledge_filter=None, **kwargs):
        """
        查询知识点列表
        该接口可返回知识点相关信息，具体内容包含知识点所在分类、知识点标准问以及相似问。
        返回的知识点范围为：调用时使用的开放平台Pubkey所属的项目(APP)中的所有知识点。
        Filter字段如果不传入，则返回所有知识点。
        Filter.knowledge_tag_id 字段如果传入，返回该分类下的所有知识点, 但不包含该分类的子分类下的知识点。
        Filter.knowledge_id 和 Filter.knowledge_tag_id 如果同时传入，则返回两个条件都满足的知识点。
        因此，如果传入的 knowledge_id 所代表的知识点不属于传入的 knowledge_tag_id 所代表的知识点分类，则不会返回任何结果。
        :param page: int (页码，代表查看第几页的数据)
        :param page_size: int (每页的知识点数量)
        :param knowledge_filter: dict (过滤条件)
        {
            "knowledge_id": str(知识点id，如不填写，返回所有知识点)
            "knowledge_tag_id": str(知识点分类id，如不填写，返回所有知识点分类下知识点)
        }
        :return:
        """
        params = {
            "filter": knowledge_filter,
            "page": page,
            "page_size": page_size,
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/qa/knowledge-items/list", params, opts)
        body = self.process_common_request(request)
        return KnowledgeItems.from_dict(body)

    def batch_create_knowledge(self, knowledge_items: list, **kwargs):
        """
        批量添加知识点列表
        批量添加知识点列表
        :param knowledge_items: list (知识点)
        [{
            "knowledge_tag": dict(知识点分类),
            "similar_questions": list(相似问详情),
            "user_attribute_group_answers": list(属性组),
            "knowledge": dict(知识点详情),
        }, ...]
        knowledge_tag:
        {
            "parent_knowledge_tag_id"【required】: str(父节点分类id),
            "id"【required】: str(知识点分类id),
            "name"【required】: str(知识点分类名)
        }
        similar_questions:
        [{
            "knowledge_id"【required】: str(知识点id),
            "question"【required】: str(相似问), <= 100characters
            "id": str(相似问id)
        }, ...]
        user_attribute_group_answers:
        [{
            "answer"【required】: (回复){
                "knowledge_id"【required】: str(知识点id),
                "msg_body"【required】: dict(消息体格式，任意选择一种消息类型（文本 / 图片 / 语音 / 视频 / 文件 / 图文 / 自定义消息）填充)
            }，
            "user_attribute_group_id"【required】: str(属性组 id。
                当 id 为0时，表示该不区分属性组。使用属性组 id 为0添加的回复，是知识点的通用答案。)
        }]
        knowledge:
        {
            "status"【required】: bool(知识点状态),
                            True: 已生效
                            False: 未生效
            "update_time": str(修改时间，秒级时间戳),
            "maintained_by_user_attribute_group"【required】: bool(该属性是否被用于定义属性组),
                            True：该属性是定义属性组所使用的属性之一
                            False：该属性不被用于定义属性组
            "standard_question"【required】: str(知识点标题),
            "create_time": str(创建时间，秒级时间戳),
            "respond_all"【required】: bool(是否发送全部回复),
                            True：发送全部回复
                            False：随机一条发送
            "id": str(知识点id)
        }
        :return:
        """
        params = {
            "knowledge_items": knowledge_items
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/qa/knowledge-items/batch-create", params, opts)
        body = self.process_common_request(request)
        return KnowledgeBatchCreate.from_dict(body)

    def create_knowledge_tag(self, knowledge_tag: dict, **kwargs):
        """
        创建知识点分类
        新增一个知识点分类。父节点分类id如果不传值，代表创建根节点下的一级知识点分类；父节点分类id如果传值，代表创建该父节点分类下的子分类。
        :param knowledge_tag: dict (知识点分类)
        {
            "parent_knowledge_tag_id"【required】: str (父节点分类id)
            "id"【required】: str(知识点分类id)
            "name"【required】: str(知识点分类名)
        }
        :return:
        """
        params = {
            "knowledge_tag": knowledge_tag
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/qa/knowledge-tag/create", params, opts)
        body = self.process_common_request(request)
        return KnowledgeTagCreate.from_dict(body)

    def update_knowledge_tag(self, knowledge_tag: dict, **kwargs):
        """
        更新知识点分类
        更新一个知识点分类。父节点分类id和知识点分类名如果不传值，代表不变更。
        :param knowledge_tag: dict (知识点分类)
        {
            "id"【required】: str(知识点分类id)
            "name"【required】: str(知识点分类名)
        }
        :return:
        """
        params = {
            "knowledge_tag": knowledge_tag
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/qa/knowledge-tag/update", params, opts)
        body = self.process_common_request(request)
        return KnowledgeTagUpdate.from_dict(body)

    def delete_knowledge_tag(self, knowledge_tag_id: int, **kwargs):
        """
        删除知识点分类
        删除知识点分类
        :param knowledge_tag_id: int (知识点分类id)
        :return:
        """
        params = {
            "id": knowledge_tag_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/qa/knowledge-tag/delete", params, opts)
        body = self.process_common_request(request)
        return body

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
        注:
        只有当知识点id已经在吾来平台中创建后，才可通过该接口创建属性组回复。如果知识点id尚未在系统中创建，则无法成功创建属性组回复
        如需创建知识点详情中的通用答案（不区分属性组），则 user_attribute_group_id 传入0.
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
        注:
        如需更新知识点的通用答案（不区分属性组），则 user_attribute_group_id 传入0.
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

    # 统计类
    def create_qa_satisfaction(
            self, msg_id: str, user_id: str, bot_id: dict, satisfaction="DEFAULT_SATISFACTION", **kwargs
    ):
        """
        添加用户满意度评价
        该接口用于写入用户的满意度评价。
        :param msg_id: str(机器人回复的消息id)
        :param user_id: str(用户id)
        :param bot_id: dict(机器人id，选择其中一种填写)
        :param satisfaction: str(满意度枚举类型)
        bot_id:
        {
            "knowledge_id": str(知识点id)
        }
        satisfaction: one of
            THUMB_UP: 点赞
            BAD_ANSWER: 回答了我的问题，但答案不够好
            WRONG_ANSWER: 没有回答我的问题
            REPORT: 举报
        :return:
        """
        params = {
            "msg_id": msg_id,
            "user_id": user_id,
            "bot_id": bot_id,
            "satisfaction": satisfaction,
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/qa/satisfaction/create", params, opts)
        body = self.process_common_request(request)
        return body

    def stats_qa_satisfaction_daily_knowledges(
            self, start_date: str, end_date: str, page: int, page_size: int, **kwargs
    ):
        """
        查询问答满意度评价统计列表（知识点粒度，日报）
        该接口可按照开始和结束日期查询每个知识点每天的满意度统计。满意度数据分为：点赞、答案不满意、答非所问三类。

        注:开始时间和结束时间相距不能超过30天。
        :param start_date: str(开始日期，格式如19700101。闭区间。开始时间和结束时间相距不能超过30天)
        :param end_date: str(结束日期，格式如19700101。闭区间。结束时间需小于当天，开始时间和结束时间相距不能超过30天)
        :param page: int(页码，代表查看第几页的数据 >=1)
        :param page_size: int(每页的知识点数量 [1..200])
        :return:
        """
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "page": page,
            "page_size": page_size,
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/stats/qa/satisfaction/daily/knowledge/list", params, opts)
        body = self.process_common_request(request)
        return StatsQASatisfactionKnowledgeDaily.from_dict(body)

    def stats_qa_recall_daily(self, start_date: str, end_date: str, **kwargs):
        """
        查询问答召回数统计列表（日报）
        该接口可按照开始和结束日期查询每天的接收消息总数和召回总数。

        注:开始时间和结束时间相距不能超过30天。
        :param start_date: str(开始日期，格式如19700101。闭区间。开始时间和结束时间相距不能超过30天)
        :param end_date: str(结束日期，格式如19700101。闭区间。结束时间需小于当天，开始时间和结束时间相距不能超过30天)
        :return:
        """
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/stats/qa/recall/daily/list", params, opts)
        body = self.process_common_request(request)
        return StatsQARecallDaily.from_dict(body)

    def stats_qa_recall_daily_knowledges(
            self, start_date: str, end_date: str, page: int, page_size: int, **kwargs
    ):
        """
        查询问答召回数统计列表（知识点粒度，日报）
        该接口可按照开始和结束日期查询每个知识点每天的召回数统计。

        注:开始时间和结束时间相距不能超过30天。
        :param start_date: str(开始日期，格式如19700101。闭区间。开始时间和结束时间相距不能超过30天)
        :param end_date: str(结束日期，格式如19700101。闭区间。结束时间需小于当天，开始时间和结束时间相距不能超过30天)
        :param page: int(页码，代表查看第几页的数据 >=1)
        :param page_size: int(每页的知识点数量 [1..200])
        :return:
        """
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "page": page,
            "page_size": page_size,
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/stats/qa/recall/daily/knowledge/list", params, opts)
        body = self.process_common_request(request)
        return StatasQARecallDailyKnowledges.from_dict(body)

    # 词库管理类
    def dictionary_entities(self, page: int, page_size: int, **kwargs):
        """
        查询全部实体概要
        查询全部实体的概要，包括实体ID、实体名称和实体类型。
        :param page:
        :param page_size:
        :param kwargs:
        :return:
        """
        params = {
            "page": page,
            "page_size": page_size,
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/dictionary/entity/list", params, opts)
        body = self.process_common_request(request)
        return DictionaryEntities.from_dict(body)

    def dictionary_terms(self, page: int, page_size: int, **kwargs):
        """
        查询专有词汇列表
        该接口用于查询所有的专有词汇，包括定义专有词汇的id、名称和同义词。
        :param page:
        :param page_size:
        :param kwargs:
        :return:
        """
        params = {
            "page": page,
            "page_size": page_size,
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/dictionary/term/list", params, opts)
        body = self.process_common_request(request)
        return DictionaryTerms.from_dict(body)

    def create_dictionary_term(self, term_item: dict, **kwargs):
        """
        创建专有词汇
        该接口用于创建专有词汇，包括定义专有词汇的名称和同义词。
        :param term_item: dict(专有词汇)
        :param kwargs:
        term_item:
        {
            "term"【required】(专有词汇详情): {
                "name"【required】: str(专有词汇的名称)
            },
            "synonyms": list(专有词汇的同义词。同义词需拼接成string，用逗号分隔，不超过1024个字符)
        }
        :return:
        """
        params = {
            "term_item": term_item
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/dictionary/term/create", params, opts)
        body = self.process_common_request(request)
        return DictionaryTerm.from_dict(body)

    def update_dictionary_term(self, term_item: dict, **kwargs):
        """
        更新专有词汇
        该接口用于更新专有词汇，包括更新专有词汇的名称和同义词。
        :param term_item: dict(专有词汇)
        :param kwargs:
        term_item:
        {
            "term"【required】(专有词汇详情): {
                "id"【required】: int(专有词汇id)
                "name": str(专有词汇的名称。如果不传入该字段，则表示不修改名称)
            },
            "synonyms": list(专有词汇的同义词。如果不传这个字段(或传入空列表)，代表不做修改；
                如果传入非空列表，代表把以前的同义词删除，重新添加。同义词需拼接成string，用逗号分隔，不超过1024个字符)
        }
        :return:
        """
        params = {
            "term_item": term_item
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/dictionary/term/update", params, opts)
        body = self.process_common_request(request)
        return DictionaryTerm.from_dict(body)

    def delete_dictionary_term(self, term_id: str, **kwargs):
        """
        删除专有词汇
        该接口用于删除一条专有词汇。
        :param term_id: str(专有词汇id)
        :param kwargs:
        :return:
        """
        params = {
            "id": term_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/dictionary/term/delete", params, opts)
        body = self.process_common_request(request)
        return body

    def dictionary_entity(self, entity_id: int, **kwargs):
        """
        查询一个实体详情
        查询一个实体的详情，包括实体ID、实体名称、实体类型和实体值。
        :param entity_id: int(实体id)
        :param kwargs:
        :return:
        """
        params = {
            "id": entity_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/dictionary/entity/get", params, opts)
        body = self.process_common_request(request)
        return DictionaryEntity.from_dict(body)

    def create_dictionary_entity_enumeration(self, enum_entity: dict, **kwargs):
        """
        创建枚举实体
        创建一个枚举实体。
        注：枚举实体的实体值需要通过「创建枚举实体值」接口创建。
        :param enum_entity: dict(枚举实体)
        :param kwargs:
        enum_entity:
        {
            "name"【required】: str(实体名称) [ 1 .. 200 ] characters
        }
        :return:
        """
        params = {
            "enum_entity": enum_entity
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/dictionary/entity/enumeration/create", params, opts)
        body = self.process_common_request(request)
        return CreateEnumEntity.from_dict(body)

    def create_dictionary_entity_enumeration_value(self, entity_id: int, value: dict, **kwargs):
        """
        创建枚举实体值
        给一个枚举实体添加实体值，包括标准值及其相似说法。
        :param entity_id: int(实体id)
        :param value: dict(枚举实体值)
        :param kwargs:
        value:
        {
            "synonyms": list(标准值的相似说法),
            "standard_value"【required】: str(标准值(归一化值)) [ 1 .. 200 ] characters
        }
        :return:
        """
        params = {
            "entity_id": entity_id,
            "value": value
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/dictionary/entity/enumeration/value/create", params, opts)
        body = self.process_common_request(request)
        return CreateEnumEntityValue.from_dict(body)

    def delete_dictionary_entity_enumeration_value(self, entity_id: int, value: dict, **kwargs):
        """
        删除枚举实体值
        删除枚举实体的一个实体值，或实体值的若干相似说法。
        如果 value 中只传入了 standard_value，会删除这个实体值和其对应的所有相似说法；
        如果 value 中传入了standard_value 和 synonyms，会删除这个实体值中 synonym 传入的相似说法。
        :param entity_id: int(实体id)
        :param value: dict(枚举实体值)
        :param kwargs:
        value:
        {
            "synonyms": list(标准值的相似说法),
            "standard_value"【required】: str(标准值(归一化值)) [ 1 .. 200 ] characters
        }
        :return:
        """
        params = {
            "entity_id": entity_id,
            "value": value
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/dictionary/entity/enumeration/value/delete", params, opts)
        body = self.process_common_request(request)
        return body

    def create_dictionary_entity_intent(self, intent_entity: dict, **kwargs):
        """
        创建意图实体
        创建一个意图实体，及其标准值。
        注：意图实体的相似说法需要通过「创建意图实体值相似说法」接口创建。
        :param intent_entity: dict(意图实体)
        :param kwargs:
        intent_entity:
        {
            "standard_value"【required】: str(标准值) [ 1 .. 200 ] characters
            "name"【required】: str(实体名称) [ 1 .. 200 ] characters
        }
        :return:
        """
        params = {
            "intent_entity": intent_entity
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/dictionary/entity/intent/create", params, opts)
        body = self.process_common_request(request)
        return CreateIntentEntity.from_dict(body)

    def create_dictionary_entity_intent_value(self, entity_id: int, synonyms: list, **kwargs):
        """
        创建意图实体值相似说法
        给一个意图实体添加相似说法。
        :param entity_id: int(实体id)
        :param synonyms: list(意图实体值的相似说法) [ 1 .. 200 ] characters
        :param kwargs:
        :return:
        """
        params = {
            "entity_id": entity_id,
            "synonyms": synonyms
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/dictionary/entity/intent/value/create", params, opts)
        body = self.process_common_request(request)
        return CreateIntentEntityValue.from_dict(body)

    def delete_dictionary_entity_intent_value(self, entity_id: int, synonyms: list, **kwargs):
        """
        删除意图实体值相似说法
        :param entity_id: int(实体id)
        :param synonyms: list(意图实体值的相似说法) [ 1 .. 200 ] characters
        :param kwargs:
        :return:
        """
        params = {
            "entity_id": entity_id,
            "synonyms": synonyms
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/dictionary/entity/intent/value/delete", params, opts)
        body = self.process_common_request(request)
        return body

    def delete_dictionary_entity(self, entity_id: int, **kwargs):
        """
        删除实体
        删除一个实体。
        注：预设实体不可删除。
        :param entity_id: int(实体id)
        :param kwargs:
        :return:
        """
        params = {
            "id": entity_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/dictionary/entity/delete", params, opts)
        body = self.process_common_request(request)
        return body

    # 自然语言处理类
    def entities_extract(self, query: str, **kwargs):
        """
        实体抽取
        该接口用于实体抽取。
        :param query: str(待实体抽取query)
        :param kwargs:
        :return:
        """
        params = {
            "query": query
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/nlp/entities/extract", params, opts)
        body = self.process_common_request(request)
        return EntityExtract.from_dict(body)

    def tokenize(self, query: str, **kwargs):
        """
        分词&词性标注
        该接口用于分词以及词性标注。
        :param query: str(待分词的query [ 1 .. 1024 ] characters)
        :param kwargs:
        :return:
        """
        params = {
            "query": query
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/nlp/tokenize", params, opts)
        body = self.process_common_request(request)
        return Tokenize.from_dict(body)

    def mining_upload(self, queries: list, **kwargs):
        """
        导入待聚类语料
        该接口用于上传待聚类语料。语料可多次添加，再一起执行聚类。
        如需覆盖已经导入的语料，请先调用「清空待聚类语料接口」清空语料，然后再上传新语料。
        单次上传的上限为1千条。如果超限只截取前1千条。 发起一次聚类的语料总上限为5万。如果超限只截取前5万条。
        :param queries: list(待聚类语料)
        :param kwargs:
        :return:
        """
        params = {
            "queries": queries
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/nlp/sentence/mining/upload", params, opts)
        body = self.process_common_request(request)
        return MiningUpload.from_dict(body)

    def mining_empty(self, **kwargs):
        """
        清空待聚类语料
        该接口用于清空待聚类语料库。
        :param kwargs:
        :return:
        """
        params = {}
        opts = self.opts_create(kwargs)

        request = CommonRequest("/nlp/sentence/mining/empty", params, opts)
        body = self.process_common_request(request)
        return body

    def mining_execute(self, **kwargs):
        """
        发起聚类
        该接口用于发起聚类请求。发起一次聚类的语料总上限为5万。
        如果超限只截取前5万条。 在发起聚类请求后，下一步调用「获取聚类结果列表接口」查询聚类是否完成和聚类结果。
        如果在一次聚类请求未完成时发起第二次聚类，当所有聚类完成后，「获取聚类结果列表接口」只会返回最后一次聚类的结果。
        :param kwargs:
        :return:
        """
        params = {}
        opts = self.opts_create(kwargs)

        request = CommonRequest("/nlp/sentence/mining/execute", params, opts)
        body = self.process_common_request(request)
        return MiningExecute.from_dict(body)

    def mining_result(self, page: int, page_size: int, **kwargs):
        """
        获取聚类结果列表
        该接口用于获取聚类结果。 如果当前最后一次请求在进行中，则返回的状态为“进行中”，结果为空。
        如果当前最后一次请求已完成，则返回的状态为“完成”，结果为最后一次聚类的结果。
        如果在一次聚类请求未完成时发起第二次聚类，当所有聚类完成后，接口只会返回最后一次聚类的结果。
        :param page: int(页码)
        :param page_size: int(每页中簇的数量)
        :param kwargs:
        :return:
        """
        params = {
            "page": page,
            "page_size": page_size
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/nlp/sentence/mining/result/get", params, opts)
        body = self.process_common_request(request)
        return MiningResult.from_dict(body)

    def delete_mining_sentence(self, sentence_id: int, **kwargs):
        """
        删除聚类结果
        该接口用于删除聚类结果中的一个句子。
        :param sentence_id: int(句子ID)
        :param kwargs:
        :return:
        """
        params = {
            "id": sentence_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/nlp/sentence/mining/sentence/delete", params, opts)
        body = self.process_common_request(request)
        return body

    # 任务类
    def scenes(self, **kwargs):
        """
        查询场景列表
        查询任务对话中的所有场景。
        :param kwargs:
        :return:
        """
        params = {}
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/list", params, opts)
        body = self.process_common_request(request)
        return Scenes.from_dict(body)

    def create_scene(self, scene: dict, **kwargs):
        """
        创建场景
        创建任务对话中的一个场景。
        :param scene: dict(任务)
        :param kwargs:
        scene:
        {
            "intent_switch_mode"【required】: str(意图切换模式(在意图流程中，当用户消息既可以在当前意图中填槽、又可以触发其他意图时，优先选择的处理方式。).),
                INTENT_SWITCH_MODE_SWITCH: 优先切换到其他意图
                INTENT_SWITCH_MODE_STAY: 优先停留在当前意图并填槽
            "name"【required】: str(场景名称) [ 1 .. 200 ] characters,
            "smart_slot_filling_threshold": float(智能填槽阈值) <= 1,
            "description": str(场景描述) <= 600 characters
        }
        :return:
        """
        params = {
            "scene": scene
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/create", params, opts)
        body = self.process_common_request(request)
        return CreateScene.from_dict(body)

    def update_scene(self, scene: dict, **kwargs):
        """
        更新场景
        更新任务对话中的一个场景。
        :param scene: dict(任务)
        :param kwargs:
        scene:
        {
            "intent_switch_mode": str(意图切换模式(在意图流程中，当用户消息既可以在当前意图中填槽、又可以触发其他意图时，优先选择的处理方式。).),
                INTENT_SWITCH_MODE_SWITCH: 优先切换到其他意图
                INTENT_SWITCH_MODE_STAY: 优先停留在当前意图并填槽
            "name": str(场景名称) [ 1 .. 200 ] characters,
            "smart_slot_filling_threshold": float(智能填槽阈值) <= 1,
            "description": str(场景描述) <= 600 characters,
            "id"【required】: int(场景ID) >= 1
        }
        :return:
        """
        params = {
            "scene": scene
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/update", params, opts)
        body = self.process_common_request(request)
        return UpdateScene.from_dict(body)

    def delete_scene(self, scene_id: int, **kwargs):
        """
        删除场景
        删除任务对话中的一个场景。
        :param scene_id: int(场景ID) >= 1
        :param kwargs:
        :return:
        """
        params = {
            "id": scene_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/delete", params, opts)
        body = self.process_common_request(request)
        return body

    def intents(self, scene_id: int, **kwargs):
        """
        查询意图列表
        查询一个场景下的所有意图。
        :param scene_id: int(意图所属的场景ID) >= 1
        :param kwargs:
        :return:
        """
        params = {
            "scene_id": scene_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/intent/list", params, opts)
        body = self.process_common_request(request)
        return Intents.from_dict(body)

    def create_intent(self, intent: dict, **kwargs):
        """
        创建意图
        创建场景下的一个意图。
        注: 只有当一个场景已经在吾来平台中创建后，才可在当前接口中传入其ID。如果场景ID尚未创建，则无法成功创建意图。
        :param intent: dict(意图)
        :param kwargs:
        intent:
        {
            "scene_id"【required】: int(意图所属场景ID) >= 1,
            "name"【required】: str(意图名称) [1 .. 200 ] characters,
            "lifespan_mins": int(意图闲置等待时长（分钟），默认3分钟) <= 60
        }
        :return:
        """
        params = {
            "intent": intent
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/intent/create", params, opts)
        body = self.process_common_request(request)
        return CreateIntent.from_dict(body)

    def update_intent(self, intent: dict, **kwargs):
        """
        更新意图
        更新场景下的一个意图。
        :param intent: dict(意图)
        :param kwargs:
        intent:
        {
            "id"【required】: int(意图ID) >= 1,
            "name": str(意图名称) [1 .. 200 ] characters,
            "lifespan_mins": int(意图闲置等待时长（分钟），默认3分钟) <= 60
        }
        :return:
        """
        params = {
            "intent": intent
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/intent/update", params, opts)
        body = self.process_common_request(request)
        return UpdateIntent.from_dict(body)

    def delete_intent(self, intent_id: int, **kwargs):
        """
        删除意图
        删除场景下的一个意图。
        :param intent_id: int(意图ID) >= 1
        :param kwargs:
        :return:
        """
        params = {
            "id": intent_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/intent/delete", params, opts)
        body = self.process_common_request(request)
        return body

    def intent_triggers(self, intent_id: int, page: int, page_size: int, **kwargs):
        """
        查询触发器列表
        查询一个意图中的所有触发器内容。
        :param intent_id: int(意图ID) >= 1
        :param page: int (页码，代表查看第几页的数据，从1开始) >= 1
        :param page_size: int (每页的触发器数量) [ 1 .. 200 ]
        :param kwargs:
        :return:
        """
        params = {
            "intent_id": intent_id,
            "page": page,
            "page_size": page_size,
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/intent/trigger/list", params, opts)
        body = self.process_common_request(request)
        return IntentTriggers.from_dict(body)

    def create_intent_trigger(self, intent_trigger: dict, **kwargs):
        """
        创建触发器
        创建一条触发器内容。触发器的文本匹配模式可以选择：完全匹配的关键词，包含匹配的关键词，或者相似说法。
        :param intent_trigger: dict(触发器)
        :param kwargs:
        intent:
        {
            "intent_id"【required】: int(触发器对应的意图ID) >= 1,
            "text"【required】: str(触发文本) [1 .. 200 ] characters,
            "type"【required】: str(触发器模式.)
                            TRIGGER_TYPE_ERROR: 错误
                            TRIGGER_TYPE_EXACT_MATCH_KEYWORD: 关键词完全匹配
                            TRIGGER_TYPE_INCLUDE_KEYWORD: 关键词包含匹配
                            TRIGGER_TYPE_SENTENCE: 相似说法
        }
        :return:
        """
        params = {
            "intent_trigger": intent_trigger
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/intent/trigger/create", params, opts)
        body = self.process_common_request(request)
        return CreateIntentTrigger.from_dict(body)

    def update_intent_trigger(self, intent_trigger: dict, **kwargs):
        """
        更新触发器
        更新一条触发器内容。
        :param intent_trigger: dict(触发器)
        :param kwargs:
        intent:
        {
            "id"【required】: int(触发器ID) >= 1,
            "text": str(触发文本) [1 .. 200 ] characters,
        }
        :return:
        """
        params = {
            "intent_trigger": intent_trigger
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/intent/trigger/update", params, opts)
        body = self.process_common_request(request)
        return UpdateIntentTrigger.from_dict(body)

    def delete_intent_trigger(self, intent_trigger_id: int, **kwargs):
        """
        删除触发器
        删除一条触发器内容。
        :param intent_trigger_id: int(触发器ID) >= 1
        :param kwargs:
        :return:
        """
        params = {
            "id": intent_trigger_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/intent/trigger/delete", params, opts)
        body = self.process_common_request(request)
        return body

    def slots(self, scene_id: int, page: int, page_size: int, **kwargs):
        """
        查询词槽列表
        查询一个场景下的所有词槽ID和词槽名称。
        :param scene_id: int(词槽所属的场景ID) >= 1
        :param page: int (页码，代表查看第几页的数据，从1开始) >= 1
        :param page_size: int (每页的词槽数量) [ 1 .. 200 ]
        :param kwargs:
        :return:
        """
        params = {
            "scene_id": scene_id,
            "page": page,
            "page_size": page_size
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/slot/list", params, opts)
        body = self.process_common_request(request)
        return Slots.from_dict(body)

    def create_slot(self, slot: dict, **kwargs):
        """
        创建词槽
        创建词槽，包括设置词槽是否允许整句填槽。

        注：整句填槽指的是，当未识别到引用实体时，将用户的整句话填充到词槽。
        :param slot: dict(词槽)
        :param kwargs:
        slot:
        {
            "scene_id"【required】: int(词槽所属的场景ID) >= 1,
            "name"【required】: str(词槽名称) [ 1 .. 200 ] characters,
            "query_slot_filling": bool (是否允许整句填槽, 默认关闭)
                                True: 开启
                                False: 关闭
        }
        :return:
        """
        params = {
            "slot": slot
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/slot/create", params, opts)
        body = self.process_common_request(request)
        return CreateSlot.from_dict(body)

    def update_slot(self, slot: dict, **kwargs):
        """
        更新词槽
        更新词槽。
        :param slot: dict(词槽)
        :param kwargs:
        slot:
        {
            "id"【required】: int(词槽ID),
            "name": str(词槽名称) [ 1 .. 200 ] characters,
            "query_slot_filling": bool (是否允许整句填槽, 默认关闭)
                                True: 开启
                                False: 关闭
        }
        :return:
        """
        params = {
            "slot": slot
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/slot/update", params, opts)
        body = self.process_common_request(request)
        return UpdateSlot.from_dict(body)

    def get_slot(self, slot_id: int, **kwargs):
        """
        查询词槽
        查询一个词槽的详情。
        :param slot_id: int(词槽ID) >= 1
        :param kwargs:
        :return:
        """
        params = {
            "id": slot_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/slot/get", params, opts)
        body = self.process_common_request(request)
        return GetSlot.from_dict(body)

    def delete_slot(self, slot_id: int, **kwargs):
        """
        删除词槽
        删除词槽。
        :param slot_id: int(词槽ID) >= 1
        :param kwargs:
        :return:
        """
        params = {
            "id": slot_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/slot/delete", params, opts)
        body = self.process_common_request(request)
        return body

    def slot_data_source(self, slot_id: int, **kwargs):
        """
        查询词槽数据来源
        查询一个词槽的所有数据来源。
        :param slot_id: int(词槽ID) >= 1
        :param kwargs:
        :return:
        """
        params = {
            "slot_id": slot_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/slot/data-source/list", params, opts)
        body = self.process_common_request(request)
        return SlotDataSource.from_dict(body)

    def create_slot_data_source(self, data_source: dict, **kwargs):
        """
        创建词槽数据来源
        创建词槽数据来源即定义词槽的引用实体，将实体与词槽关联起来。

        注：必须先创建词槽和实体后，才可以创建词槽数据来源。
        :param data_source: dict(词槽数据来源)
        :param kwargs:
        data_source:
        {
            "entity_id"【required】: int (实体ID) >= 1,
            "slot_id"【required】: int (词槽ID) >= 1
        }
        :return:
        """
        params = {
            "data_source": data_source
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/slot/data-source/create", params, opts)
        body = self.process_common_request(request)
        return CreateSlotDataSource.from_dict(body)

    def delete_slot_data_source(self, slot_data_source_id: int, **kwargs):
        """
        删除词槽数据来源
        删除词槽数据来源。
        :param slot_data_source_id: int(词槽数据来源ID) >= 1
        :param kwargs:
        :return:
        """
        params = {
            "id": slot_data_source_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/slot/data-source/delete", params, opts)
        body = self.process_common_request(request)
        return body

    def inform_block(self, block_id: int, **kwargs):
        """
        查询消息发送单元
        查询一个消息发送单元的详情，包括单元设置、单元回复、和该单元与其他单元的跳转关系。
        :param block_id: int(单元ID) >= 1
        :param kwargs:
        :return:
        """
        params = {
            "id": block_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/block/inform-block/get", params, opts)
        body = self.process_common_request(request)
        return GetInformBlock.from_dict(body)

    def create_inform_block(self, block: dict, **kwargs):
        """
        创建消息发送单元
        创建一个消息发送单元。
        :param block: dict (消息发送单元)
        :param kwargs:
        block:
        {
            "intent_id"【required】: int (所属意图ID) >= 1,
            "name"【required】: str (单元名称) [ 1 .. 200 ] characters,
            "mode"【required】: str (单元回复类型.)
                            RESPONSE_ERROR: 错误
                            RESPONSE_RANDOM: 随机回复
                            RESPONSE_ALL: 全部回复
                            RESPONSE_LOOP: 依次回复
        }
        :return:
        """
        params = {
            "block": block
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/block/inform-block/create", params, opts)
        body = self.process_common_request(request)
        return CreateInformBlock.from_dict(body)

    def update_inform_block(self, block: dict, **kwargs):
        """
        更新消息发送单元
        更新一个消息发送单元。
        :param block: dict (消息发送单元)
        :param kwargs:
        block:
        {
            "id"【required】: int (单元ID) >= 1,
            "name": str (单元名称) [ 1 .. 200 ] characters,
            "mode": str (单元回复类型.)
                RESPONSE_ERROR: 错误
                RESPONSE_RANDOM: 随机回复
                RESPONSE_ALL: 全部回复
                RESPONSE_LOOP: 依次回复
        }
        :return:
        """
        params = {
            "block": block
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/block/inform-block/update", params, opts)
        body = self.process_common_request(request)
        return UpdateInformBlock.from_dict(body)

    def request_block(self, block_id: int, **kwargs):
        """
        查询询问填槽单元
        查询一个询问填槽单元的详情，包括单元设置、单元回复、该单元与其他单元的跳转关系等。

        注：必须先创建一个词槽，才可以在单元中使用它作为关联词槽。
        :param block_id: int(单元ID) >= 1
        :param kwargs:
        :return:
        """
        params = {
            "id": block_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/block/request-block/get", params, opts)
        body = self.process_common_request(request)
        return GetRequestBlock.from_dict(body)

    def create_request_block(self, block: dict, **kwargs):
        """
        创建询问填槽单元
        创建一个询问填槽单元。

        注：必须先创建一个词槽，才可以在单元中使用它作为关联词槽。
        :param block: dict (询问填槽单元)
        :param kwargs:
        block:
        {
            "intent_id"【required】: int (所属意图ID) >= 1,
            "name"【required】: str (单元名称) [ 1 .. 200 ] characters,
            "slot_id"【required】: int (绑定的词槽ID) >= 1,
            "default_slot_value": str (默认词槽值) <= 200 characters,
            "slot_filling_when_asked": bool (是否仅询问时填槽),
                                    默认否
                                    True: 仅在当前单元询问时才填充关联词槽
                                    False: 即使机器人并没有询问，如果用户消息中有可以填槽的信息，也填充关联词槽
            "mode"【required】: str (单元回复类型.),
                            RESPONSE_ERROR: 错误
                            RESPONSE_RANDOM: 随机回复
                            RESPONSE_ALL: 全部回复
                            RESPONSE_LOOP: 依次回复
            "request_count": int (询问次数，默认3次) <= 200
        }
        :return:
        """
        params = {
            "block": block
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/block/request-block/create", params, opts)
        body = self.process_common_request(request)
        return CreateRequestBlock.from_dict(body)

    def update_request_block(self, block: dict, **kwargs):
        """
        更新询问填槽单元
        更新一个询问填槽单元。

        注：必须先创建一个词槽，才可以在单元中使用它作为关联词槽。
        :param block: dict (询问填槽单元)
        :param kwargs:
        block:
        {
            "id"【required】: int (单元ID) >= 1,
            "name": str (单元名称) [ 1 .. 200 ] characters,
            "slot_id": int (绑定的词槽ID) >= 1,
            "default_slot_value": str (默认词槽值) <= 200 characters,
            "slot_filling_when_asked": bool (是否仅询问时填槽),
                                    默认否
                                    True: 仅在当前单元询问时才填充关联词槽
                                    False: 即使机器人并没有询问，如果用户消息中有可以填槽的信息，也填充关联词槽
            "mode": str (单元回复类型.),
                RESPONSE_ERROR: 错误
                RESPONSE_RANDOM: 随机回复
                RESPONSE_ALL: 全部回复
                RESPONSE_LOOP: 依次回复
            "request_count": int (询问次数，默认3次) <= 200
        }
        :return:
        """
        params = {
            "block": block
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/block/request-block/update", params, opts)
        body = self.process_common_request(request)
        return UpdateRequestBlock.from_dict(body)

    def create_block_response(self, response: dict, **kwargs):
        """
        创建单元内回复
        给询问填槽单元或消息发送单元添加一条回复。
        :param response: dict (单元内回复)
        :param kwargs:
        response:
        {
            "block_id"【required】: int (单元ID) >= 1,
            "response"【required】: dict (消息体格式，任意选择一种消息类型（文本 / 图片 / 语音 / 视频 / 文件 / 图文 / 自定义消息）填充)
        }
        response:
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
        卡片消息
        {
        "share_link": {
            "description": str(文字描述),
            "destination_url"【required】: str(链接目标地址),
            "cover_url"【required】: str(封面图片地址),
            "title"【required】: str(链接的文字标题)
            }
        }
        图文消息
        {"rich_text": {"resource_url"【required】: str}}
        :return:
        """
        params = {
            "response": response
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/block/response/create", params, opts)
        body = self.process_common_request(request)
        return CreateResponse.from_dict(body)

    def update_block_response(self, response: dict, **kwargs):
        """
        更新单元内回复
        给询问填槽单元或消息发送单元更新一条回复。
        :param response: dict (单元内回复)
        :param kwargs:
        response:
        {
            "id"【required】: int (回复ID) >= 1,
            "response"【required】: dict (消息体格式，任意选择一种消息类型（文本 / 图片 / 语音 / 视频 / 文件 / 图文 / 自定义消息）填充)
        }
        response:
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
        卡片消息
        {
        "share_link": {
            "description": str(文字描述),
            "destination_url"【required】: str(链接目标地址),
            "cover_url"【required】: str(封面图片地址),
            "title"【required】: str(链接的文字标题)
            }
        }
        图文消息
        {"rich_text": {"resource_url"【required】: str}}
        :return:
        """
        params = {
            "response": response
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/block/response/update", params, opts)
        body = self.process_common_request(request)
        return UpdateResponse.from_dict(body)

    def delete_block_response(self, response_id: int, **kwargs):
        """
        删除单元内回复
        删除一条单元内回复。
        :param response_id: int (回复ID) >= 1
        :param kwargs:
        :return:
        """
        params = {
            "id": response_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/block/response/delete", params, opts)
        body = self.process_common_request(request)
        return body

    def end_block(self, block_id: int, **kwargs):
        """
        查询意图终点单元
        查询一个意图终点单元的详情。
        :param block_id: int (单元ID) >= 1
        :param kwargs:
        :return:
        """
        params = {
            "id": block_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/block/end-block/get", params, opts)
        body = self.process_common_request(request)
        return GetEndBlock.from_dict(body)

    def create_end_block(self, block: dict, **kwargs):
        """
        创建意图终点单元
        创建一个意图终点单元。

        注：意图终点单元如果要跳转到一个指定意图，该意图必须先被创建。
        :param block: dict (意图终点单元)
        :param kwargs:
        block:
        {
            "action": dict(结束单元跳转方式 (指定意图 / 上个意图 / 不跳转)),
            "intent_id"【required】: int(所属意图ID) >= 1,
            "name"【required】: str(单元名称) [ 1 .. 200 ] characters,
            "slot_memorizing": bool(是否保存词槽值)
                            默认关闭
                            True: 开启
                            False: 关闭
        }
        action:
        意图终点单元跳转上个意图:
        {"last": {}}
        意图终点单元不跳转:
        {"end": {}}
        意图终点单元跳转指定意图:
        {"specified"【required】: {"id": int (意图ID) >= 1}}
        :return:
        """
        params = {
            "block": block
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/block/end-block/create", params, opts)
        body = self.process_common_request(request)
        return CreateEndBlock.from_dict(body)

    def update_end_block(self, block: dict, **kwargs):
        """
        更新意图终点单元
        更新一个意图终点单元。
        :param block: dict (意图终点单元)
        :param kwargs:
        block:
        {
            "action": dict(结束单元跳转方式 (指定意图 / 上个意图 / 不跳转)),
            "id"【required】: int(单元ID) >= 1,
            "name": str(单元名称) [ 1 .. 200 ] characters,
            "slot_memorizing": bool(是否保存词槽值)
                            默认关闭
                            True: 开启
                            False: 关闭
        }
        action:
        意图终点单元跳转上个意图:
        {"last": {}}
        意图终点单元不跳转:
        {"end": {}}
        意图终点单元跳转指定意图:
        {"specified"【required】: {"id": int (意图ID) >= 1}}
        :return:
        """
        params = {
            "block": block
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/block/end-block/update", params, opts)
        body = self.process_common_request(request)
        return UpdateEndBlock.from_dict(body)

    def blocks(self, intent_id: int, page: int, page_size: int, **kwargs):
        """
        查询单元列表
        查询意图里的所有单元。
        :param intent_id: int (意图ID) >= 1
        :param page: int (页码，代表查看第几页的数据，从1开始) >= 1
        :param page_size: int (每页的单元数量) [ 1 .. 200 ]
        :param kwargs:
        :return:
        """
        params = {
            "intent_id": intent_id,
            "page": page,
            "page_size": page_size
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/block/list", params, opts)
        body = self.process_common_request(request)
        return Blocks.from_dict(body)

    def create_block_relation(self, relation: dict, **kwargs):
        """
        创建单元关系
        创建单元与单元之间的跳转关系，包括当前单元、下一个单元、以及跳转条件。
        :param relation: dict (单元关系)
        :param kwargs:
        relation:
        {
            "connection": dict(单元关系),
            "intent_id": int(意图ID) >= 1
        }
        connection:
        {
            "from_block_id"【required】: int(当前单元ID) >= 1,
            "to_block_id"【required】: int(下一个单元ID) >= 1,
            "condition": dict(单元跳转条件(默认 / 大于 / 大于等于 / 小于 / 小于等于 / 等于 / 不等于 / 包含 / 不包含 / 属于实体 / 不属于实体 / 符合正则 / 不符合正则))
        }
        condition:
        默认
        {"default": {}}
        属于(实体)
        {"in_entity": {"id": int}}
        不属于(实体)
        {"not_in_entity": {"id": int}}
        等于
        {"equal_to": {"value": str}}
        不等于
        {"not_equal_to": {"value": str}}
        大于
        {"greater_than": {"value": float}}
        大于等于
        {"greater_than_or_equal_to": {"value": float}}
        小于
        {"less_than": {"value": float}}
        小于等于
        {"less_than_or_equal_to": {"value": float}}
        包含
        {"include": {"value": str}}
        不包含
        {"exclude": {"value": str}}
        符合正则
        {"match_regex": {"regex": str}}
        不符合正则
        {"dismatch_regex": {"regex": str}}
        :return:
        """
        params = {
            "relation": relation
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/block/relation/create", params, opts)
        body = self.process_common_request(request)
        return CreateBlockRelation.from_dict(body)

    def delete_block_relation(self, relation_id: int, **kwargs):
        """
        删除单元关系
        删除一条单元与单元之间的跳转关系。
        :param relation_id: int (单元关系ID) >= 1
        :param kwargs:
        :return:
        """
        params = {
            "id": relation_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/block/relation/delete", params, opts)
        body = self.process_common_request(request)
        return body

    def delete_block(self, block_id: int, **kwargs):
        """
        删除单元
        删除一个对话单元，支持所有类型的单元。
        :param block_id: int (单元ID) >= 1
        :param kwargs:
        :return:
        """
        params = {
            "id": block_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/block/delete", params, opts)
        body = self.process_common_request(request)
        return body

    def intent_trigger_learning(self, page: int, page_size: int, **kwargs):
        """
        查询任务待审核消息列表
        查询触发意图的待审核消息列表。
        :param page: int (页码，代表查看第几页的数据，从1开始) >= 1
        :param page_size: int (每页的用户消息数量) [ 1 .. 200 ]
        :param kwargs:
        :return:
        """
        params = {
            "page": page,
            "page_size": page_size
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/intent/trigger-learning/list", params, opts)
        body = self.process_common_request(request)
        return IntentTriggerLearning.from_dict(body)

    def delete_intent_trigger_learning(self, msg_id: int, **kwargs):
        """
        删除任务待审核消息
        删除一条触发意图的待审核消息。
        :param msg_id: int (待审核消息ID) >= 1
        :param kwargs:
        :return:
        """
        params = {
            "id": msg_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/intent/trigger-learning/delete", params, opts)
        body = self.process_common_request(request)
        return body

    def update_intent_status(self, status: bool, first_block_id: int, intent_id: int, **kwargs):
        """
        更新意图状态
        将意图生效或者下线，同时需要指定意图的第一个单元。
        :param status: bool (意图状态,意图生成时默认未生效)
                    False: 未生效
                    True: 已生效
        :param first_block_id: int (该意图的第一个单元ID) >= 1
        :param intent_id: int (意图ID) >= 1
        :param kwargs:
        :return:
        """
        params = {
            "status": status,
            "first_block_id": first_block_id,
            "intent_id": intent_id
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/scene/intent/status/update", params, opts)
        body = self.process_common_request(request)
        return UpdateIntentStatus.from_dict(body)

    # 配置类
    def update_config(self, app_config: dict, **kwargs):
        """
        更新机器人回复配置
        更新机器人配置。
        :param app_config: dict (机器人配置)
        {
            "bot_config": dict(对话配置),
            "default_response_config": dict(兜底回复配置),
            "customer_service_config": dict(转人工配置)
        }
        bot_config:
        {
            # 问答对话配置
            "qa_bot_config": {
                "similar_response_enabled": bool(机器人回复是否包含推荐知识点),
                                        False：不包含
                                        True：包含
                "auto_response_threshold": float(问答对话的回复阈值) <= 1
            },
            # 任务对话配置
            "task_bot_config": {
                "auto_response_threshold": float(任务对话的回复阈值) <= 1
            }
        }
        default_response_config:
        {
            "enabled": bool(兜底回复开关)
                    False：关闭
                    True：开启
        }
        customer_service_config:
        {
            "enabled": bool(是否转人工)
                    False：关闭
                    True：开启
        }
        :param kwargs:
        :return:
        """
        params = {
            "app_config": app_config
        }
        opts = self.opts_create(kwargs)

        request = CommonRequest("/config/update", params, opts)
        body = self.process_common_request(request)
        return UpdateConfig.from_dict(body)
