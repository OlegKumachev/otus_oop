import time

import redis
import redis.exceptions


class Store:

    def __init__(
        self,
        host="localhost",
        port=6379,
        db=0,
        socket_timeout: float = 5,
        socket_connect_timeout: float = 10,
        max_retry: int = 5,
    ):

        self.host = host
        self.port = port
        self.db = db
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout
        self.max_retry = max_retry

        self._client = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            socket_timeout=self.socket_timeout,
            socket_connect_timeout=self.socket_connect_timeout,
        )

    def _retry(self, func, *args, **kwargs):
        for attempt in range(self.max_retry):
            try:
                return func(*args, **kwargs)
            except redis.exceptions.ConnectionError:
                if attempt == self.max_retry - 1:
                    raise
                time.sleep(0.1)

    def set(self, key, value):
        return self._retry(self._client.set, key, value)

    def get(self, key):
        return self._retry(self._client.get, key)

    def cache_get(self, key):
        try:
            return self._retry(self._client.get, key)
        except redis.exceptions.ConnectionError:
            return None

    def cache_set(self, key, value, ttl):
        try:
            return self._retry(self._client.set, key, value, ex=ttl)
        except redis.exceptions.ConnectionError:
            return None
