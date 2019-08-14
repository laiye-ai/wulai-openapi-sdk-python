from wulaisdk.exceptions import ClientException, ERR_INFO


class CommonRequest:

    def __init__(self, action, params, opts):
        """

        :param action:
        :param params:
        :param opts:
        """
        self.path = ""
        self.headers = {}
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
        # user
        if self.action == "userCreate":
            path = "/user/create"
        elif self.action == "userAttributeList":
            path = "/user-attribute/list"
        elif self.action == "userAtrributeCreate":
            path = "/user/user-attribute/create"
        # talk
        elif self.action == "getBotResponse":
            path = "/msg/bot-response"
        elif self.action == "getKeywordBotResponse":
            path = "/msg/bot-response/keyword"
        elif self.action == "getTaskBotResponse":
            path = "/msg/bot-response/task"
        elif self.action == "getQABotResponse":
            path = "/msg/bot-response/qa"
        elif self.action == "getHistoryRecord":
            path = "/msg/history"
        else:
            raise ClientException("SDK_NOT_SUPPORT", ERR_INFO["SDK_NOT_SUPPORT"])
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
