from datetime import datetime

from flask_babel import format_datetime
from flask_babel import gettext


def datetime_format(value: str) -> str:
    parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
    formatted_date = format_datetime(parsed, format="dd MMMM yyyy ")
    formatted_date += gettext("at")
    formatted_date += format_datetime(parsed, format=" HH:mm")
    formatted_date += format_datetime(parsed, "a").lower()
    return formatted_date
