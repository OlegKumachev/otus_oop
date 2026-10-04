import pytest
import redis

from scoring import get_score
from store import Store


@pytest.fixture
def store():
    s = Store()
    s._client.flushdb()
    yield s
    s._client.flushdb()


def test_store(store):
    store.set("key", "value")

    assert store.get("key") == b"value"


def test_store_cache_set_get(store):
    store.cache_set("key", "value", 60)
    assert store.cache_get("key") == b"value"


def test_store_get_missing(store):
    assert store.get("no_key") is None


def test_get_unavailable():
    store = Store(host="localhost", port=9999, max_retry=1)
    with pytest.raises(redis.exceptions.ConnectionError):
        store.get("key")


def test_get_score_with_store(store):

    score = get_score(store, phone="79175002040", email="a@b.ru")
    assert score == 3.0
