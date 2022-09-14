from datetime import datetime


def datetime_format(value):
    date_format = "%d %B %Y at %H:%M"
    am_pm_format = "%p"
    formatted_time = datetime.strptime(value, "%Y-%m-%d %X").strftime(
        date_format
    )
    formatted_time = (
        formatted_time
        + datetime.strptime(value, "%Y-%m-%d %X")
        .strftime(am_pm_format)
        .lower()
    )
    return formatted_time
