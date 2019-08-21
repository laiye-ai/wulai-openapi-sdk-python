import requests
from requests.adapters import HTTPAdapter
from wulaisdk.utils import singleton

_session = None


@singleton
class BaseRequest:

    def __init__(self, endpoint: str="https://openapi.wul.ai", method: str="POST",
                 pool_connections: int=10, pool_maxsize: int=10, max_retries: int=3):
        self.endpoint = endpoint
        self.method = method
        self.pool_connections = pool_connections
        self.pool_maxsize = pool_maxsize
        self.max_retries = max_retries

    def init_session(self):
        session = requests.Session()
        adapter = HTTPAdapter(
            pool_connections=self.pool_connections,
            pool_maxsize=self.pool_maxsize,
            max_retries=self.max_retries
        )
        session.mount(self.endpoint, adapter)
        global _session
        _session = session

    def post(self, url: str, data: dict, headers=None, timeout=3, **kwargs):
        if _session is None:
            self.init_session()
        resp = _session.post(url, json=data, headers=headers, timeout=timeout, **kwargs)
        return resp
