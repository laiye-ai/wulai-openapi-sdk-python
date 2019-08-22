import time
import uuid
import hashlib
import logging

from wulaisdk.http import BaseRequest
from wulaisdk import http_codes
from wulaisdk.request import CommonRequest
from wulaisdk.exceptions import ServerException, ClientException, ERR_INFO


DEBUG = False

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.addHandler(handler)


class WulaiClient:
    def __init__(self, pubkey: str, secret: str, endpoint: str="https://openapi.wul.ai",
                 api_version: str="v2", debug: bool=False):
        self.pubkey = pubkey
        self.secret = secret
        self.endpoint = endpoint
        self.api_version = api_version
        global DEBUG
        DEBUG = debug
        self.prepare_request()

    def prepare_request(self):
        self.check_api_version()
        self.logger_level_init()

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
                # todo: which error
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

        r = BaseRequest(self.endpoint)
        if method.upper() == "POST":
            try:
                resp = r.post(url, request.params, request.headers, timeout)
            except IOError as e:
                logger.error("HttpError occurred. Action:{} Version:{} ClientException:{}".format(
                    request.action, self.api_version, str(e)))
                raise ClientException("SDK_HTTP_ERROR", str(e))
        else:
            raise ClientException("SDK_METHOD_NOT_ALLOW", ERR_INFO["SDK_METHOD_NOT_ALLOW"])
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
            if retries < 0:
                break
        if exception:
            raise exception
        logger.debug("Response received. Action: {}. Response-body: {}".format(request.action, body))
        return body
