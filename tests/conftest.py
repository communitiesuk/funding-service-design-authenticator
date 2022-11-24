import pytest
from app import create_app
from flask import current_app
from tests.mocks import *  # noqa


@pytest.fixture
def app_context():
    with create_app().app_context():
        with current_app.test_request_context():
            yield
