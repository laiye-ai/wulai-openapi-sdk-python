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
    def __init__(self, pubkey, secret, endpoint="https://openapi.wul.ai", api_version="v2", debug=False):
        self.pubkey = pubkey
        self.secret = secret
        self.endpoint = endpoint
        self.api_version = api_version
        self.check_api_version()
        global DEBUG
        DEBUG = debug
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

    def get_headers(self, request):
        auth_headers = self.make_authentication(self.pubkey, self.secret)
        headers = request.headers
        headers.update(auth_headers)
        return headers

    def check_request(self, request):
        if not isinstance(request, CommonRequest):
            raise ClientException("SDK_INVALID_REQUEST", ERR_INFO["SDK_INVALID_REQUEST"])

    def get_url(self, request):
        url = self.endpoint + "/" + self.api_version + request.path
        return url

    # todo: 完善
    def response_wrapper(self, response):
        js = None
        exception = None
        if response is not None and response.status_code == http_codes.OK:
            js = response.json() or {}
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
        headers = self.get_headers(request)
        method = request.opts.get("method", "POST")
        timeout = request.opts.get("timeout", 3)
        logger.debug("Request received. Action: {}. Endpoint: {}. Params: {}. Opts: {}".format(
            request.action, self.endpoint, request.params, request.opts))

        r = BaseRequest(self.endpoint)
        if method.upper() == "POST":
            resp = r.post(url, request.params, headers, timeout)
        elif method.upper() == "GET":
            resp = r.get(url, request.params, headers, timeout)
        elif method.upper() == "PUT":
            resp = r.put(url, request.params, headers, timeout)
        elif method.upper() == "PATCH":
            resp = r.patch(url, request.params, headers, timeout)
        elif method.upper() == "HEAD":
            resp = r.head(url, headers, timeout)
        elif method.upper() == "DELETE":
            resp = r.delete(url, headers, timeout)
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
            time.sleep(0.1)
        if exception:
            raise exception
        logger.debug("Response received. Action: {}. Response-body: {}".format(request.action, body))
        return body
