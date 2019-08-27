from wulaisdk.exceptions import ClientException, ERR_INFO


class CommonRequest:

    def __init__(self, action: str, params: dict, opts: dict):
        """
        :param action:
        :param params:
        :param opts:
        """
        self.path = ""
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.action = action
        self.params = params
        self.opts = opts
        self.check()

    def check(self):
        self.check_action()
        self.check_params()
        self.check_opts()

    def check_action(self):
        if not isinstance(self.action, str):
            raise ClientException("SDK_NOT_SUPPORT", ERR_INFO["SDK_NOT_SUPPORT"])

    def check_params(self):
        if not isinstance(self.params, dict):
            raise ClientException("SDK_INVALID_PARAMS", ERR_INFO["SDK_INVALID_PARAMS"])

    def check_opts(self):
        if not isinstance(self.opts, dict):
            raise ClientException("SDK_INVALID_PARAMS", ERR_INFO["SDK_INVALID_PARAMS"])

    def set_headers(self, headers: dict):
        self.headers = headers

    def add_headers(self, k, v):
        self.headers[k] = v

    def update_headers(self, headers):
        self.headers.update(headers)


class CreateUserRequest(CommonRequest):
    """
    create user
    params: {"user_id": str, "avatar_url": str, "nickname": str}
    """

    def __init__(self, params: dict, opts: dict):
        super().__init__("/user/create", params, opts)


class GetBotResponseRequest(CommonRequest):
    """
    get bot response
    params: {"user_id": str, "extra": str, "msg_body": {"text": {"content": str}}}
    and msg_body must be in one of:
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
    """

    def __init__(self, params: dict, opts: dict):
        params = params or {}
        opts = opts or {}
        super().__init__("/msg/bot-response", params, opts)
