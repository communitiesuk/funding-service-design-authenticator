"""
Mock redis magic links db
"""
import pytest

ml_data = {}


class RedisMLinks(object):
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
    def get(key):
        return ml_data[key]


@pytest.fixture()
def mock_redis_magic_links(mocker):
    mocker.patch("app.redis_mlinks.setnx", RedisMLinks.setnx)
    mocker.patch("app.redis_mlinks.get", RedisMLinks.get)
    mocker.patch("app.redis_mlinks.set", RedisMLinks.set)
