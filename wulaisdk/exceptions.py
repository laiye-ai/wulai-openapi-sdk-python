class ClientException(Exception):
    _error_type = "Client"

    def __init__(self, code, msg):
        super().__init__()
        self.error_code = code
        self.error_msg = msg

    def __str__(self):
        return "{}: {}".format(self.error_code, self.error_msg)

    def set_error_code(self, code):
        self.error_code = code

    def set_error_msg(self, msg):
        self.error_msg = msg


class ServerException(Exception):
    _error_type = "Server"

    def __init__(self, code, msg, http_status_code):
        super().__init__()
        self.error_code = code
        self.error_msg = msg
        self.http_status_code = http_status_code

    def __str__(self):
        return "{} {}: {}".format(self.http_status_code, self.error_code, self.error_msg)

    def set_http_status_code(self, http_status_code):
        self.http_status_code = http_status_code

    def set_error_code(self, code):
        self.error_code = code

    def set_error_msg(self, msg):
        self.error_msg = msg


ERR_INFO = {
    "SDK_ENDPOINT_RESOLVING_ERROR": "ENDPOINT解析失败",
    "SDK_SERVER_UNREACHABLE": "无法连接服务器",
    "SDK_INVALID_REQUEST": "The request is not a valid CommonRequest.",
    "SDK_INVALID_CREDENTIAL": "The secrect or pubkey is incorrect. Please check it",
    "SDK_INVALID_PARAMS": "The param is incorrect. Please check it",
    "SDK_NOT_SUPPORT": "Invalid action, please check it",
    "SDK_HTTP_ERROR": "http request error",
    "SDK_METHOD_NOT_ALLOW": "Method not allow, please check it.",
    "SDK_INVALID_API_VERSION": "Invalid api version, please check it."
}
