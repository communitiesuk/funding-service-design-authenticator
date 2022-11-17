from datetime import datetime

from flask_babel import gettext


def _month_from_number(month_number: int) -> str:
    number_to_full_month = {
        1: gettext("January"),
        2: gettext("February"),
        3: gettext("March"),
        4: gettext("April"),
        5: gettext("May"),
        6: gettext("June"),
        7: gettext("July"),
        8: gettext("August"),
        9: gettext("September"),
        10: gettext("October"),
        11: gettext("November"),
        12: gettext("December"),
    }
    return number_to_full_month[month_number]


def datetime_format(value: str) -> str:
    at_translated = gettext("at")
    parsed = datetime.strptime(value, "%Y-%m-%d %X")
    formatted = parsed.strftime("%d ")
    formatted += _month_from_number(parsed.month)
    formatted += parsed.strftime(f" %Y {at_translated} %H:%M")
    formatted += parsed.strftime("%p").lower()
    return formatted
