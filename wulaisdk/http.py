import requests
from requests.adapters import HTTPAdapter


class BaseRequest:

    _session = None

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
        self._session = session

    def post(self, url: str, data: dict, headers: dict, timeout: int=3, **kwargs):
        if self._session is None:
            self.init_session()
        resp = self._session.post(url, json=data, headers=headers, timeout=timeout, **kwargs)
        return resp
