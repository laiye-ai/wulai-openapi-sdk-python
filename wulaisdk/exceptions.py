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


class SDK_ENDPOINT_RESOLVING_ERROR(ClientException):
    def __init__(self):
        super().__init__(code=1, msg="ENDPOINT解析失败")


class SDK_SERVER_UNREACHABLE(ClientException):
    def __init__(self):
        super().__init__(code=1, msg="无法连接服务器")


class SDK_INVALID_REQUEST(ClientException):
    def __init__(self):
        super().__init__(code=1, msg="The request is not a valid CommonRequest.")


class SDK_INVALID_CREDENTIAL(ClientException):
    def __init__(self):
        super().__init__(code=1, msg="验证信息错误")


class SDK_INVALID_PARAMS(ClientException):
    def __init__(self):
        super().__init__(code=1, msg="参数错误")


class SDK_NOT_SUPPORT(ClientException):
    def __init__(self):
        super().__init__(code=1, msg="不支持的SDK命令")


class SDK_HTTP_ERROR(ClientException):
    def __init__(self):
        super().__init__(code=1, msg="http请求错误")

