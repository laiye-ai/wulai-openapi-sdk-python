import requests
from requests.adapters import HTTPAdapter
from wulaisdk.utils import singleton


@singleton
class BaseRequest:

    _session = None

    def __init__(self, endpoint="https://openapi.wul.ai", method="POST",
                 pool_connections=10, pool_maxsize=10, max_retries=3):
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

    def post(self, url, data, headers=None, timeout=3, **kwargs):
        if self._session is None:
            self.init_session()
        resp = self._session.post(url, json=data, headers=headers, timeout=timeout, **kwargs)
        return resp

    def get(self, url, data, headers=None, timeout=3, **kwargs):
        if self._session is None:
            self.init_session()
        resp = self._session.get(url, params=data, headers=headers, timeout=timeout, **kwargs)
        return resp

    def put(self, url, data, headers=None, timeout=3, **kwargs):
        if self._session is None:
            self.init_session()
        resp = self._session.put(url, json=data, headers=headers, timeout=timeout, **kwargs)
        return resp

    def head(self, url, headers=None, timeout=3, **kwargs):
        if self._session is None:
            self.init_session()
        resp = self._session.head(url, headers=headers, timeout=timeout, **kwargs)
        return resp

    def patch(self, url, data, headers=None, timeout=3, **kwargs):
        if self._session is None:
            self.init_session()
        resp = self._session.patch(url, headers=headers, data=data, timeout=timeout, **kwargs)
        return resp

    def delete(self, url, headers=None, timeout=3, **kwargs):
        if self._session is None:
            self.init_session()
        resp = self._session.delete(url, headers=headers, timeout=timeout, **kwargs)
        return resp
