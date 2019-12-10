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
            "Content-Type": "application/json",
            # todo: version
            "User-Agent": "wulai-openapi-sdk-python/v2-1.1.6 python/3.6 requests/2.22"
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
            raise ClientException("SDK_INVALID_ACTION", ERR_INFO["SDK_INVALID_ACTION"])

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
