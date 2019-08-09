from wulaisdk.exceptions import ClientException


class CommonRequest:

    def __init__(self, action, params, opts):
        """

        :param action:
        :param params:
        :param opts:
        """
        self.path = ""
        self.action = action
        self.params = params
        self.opts = opts
        self.check()
        self.set_headers()

    def check(self):
        self.check_action()
        self.check_params()
        self.check_opts()

    def check_action(self):
        if self.action == "getBotResponse":
            path = "/msg/bot-response"
        elif self.action == "userCreate":
            path = "/user/create"
        else:
            raise ClientException("SDK_INVALID_OPTS", "Please check your action")
        self.path = path

    def check_params(self):
        return True

    def check_opts(self):
        return True

    def set_headers(self):
        base_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        if self.opts.get("headers"):
            base_headers.update(self.opts.get("headers"))
        self.headers = base_headers
