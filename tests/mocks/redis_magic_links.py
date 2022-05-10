"""
Mock redis magic links db
"""
import pytest


ml_data = {}


class RedisMLinks(object):
    @staticmethod
    def keys(match: str = "*"):
        return [link for link, value in ml_data.items()]

    @staticmethod
    def set(key, val):
        ml_data[key] = val

    @staticmethod
    def setnx(key, val):
        if key in ml_data:
            return 0
        else:
            ml_data[key] = val
            return 1

    @staticmethod
    def setex(name=None, time=None, value=None):
        ml_data[name] = value
        return 1

    @staticmethod
    def get(key):
        return ml_data.get(key)

    @staticmethod
    def delete(*names):
        for name in names:
            if ml_data.get(name):
                del ml_data[name]
        return names, ml_data


@pytest.fixture(scope="session", autouse=True)
def mock_redis_magic_links(session_mocker):
    session_mocker.patch("app.redis_mlinks.setnx", RedisMLinks.setnx)
    session_mocker.patch("app.redis_mlinks.get", RedisMLinks.get)
    session_mocker.patch("app.redis_mlinks.set", RedisMLinks.set)
    session_mocker.patch("app.redis_mlinks.setex", RedisMLinks.setex)
    session_mocker.patch("app.redis_mlinks.delete", RedisMLinks.delete)
    session_mocker.patch("app.redis_mlinks.keys", RedisMLinks.keys)
