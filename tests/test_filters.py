import pytest

import frontend.magic_links.filters as filters
from app import app


@pytest.mark.parametrize(
    "input_date, expected",
    [
        ("2020-01-01T00:00:00", "01 January 2020 at 00:00am"),
        ("2020-01-01T12:00:00", "01 January 2020 at 12:00pm"),
        ("2020-12-01T23:59:59", "01 December 2020 at 23:59pm"),
    ],
)
def test_datetime_format(input_date, expected):
    with app.test_request_context():
        assert filters.datetime_format(input_date) == expected
