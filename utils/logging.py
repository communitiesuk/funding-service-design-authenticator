from __future__ import absolute_import

import datetime
import logging
import os.path
import re
import sys
import time
from os import getpid
from threading import get_ident as get_thread_ident

from flask import current_app
from flask import request
from flask.ctx import has_request_context
from pythonjsonlogger.jsonlogger import JsonFormatter as BaseJSONFormatter

# Log formats can use any attributes available in
# https://docs.python.org/3/library/logging.html#logrecord-attributes
LOG_FORMAT = (
    "%(name)s %(levelname)s "
    "- %(message)s - from %(funcName)s in %(pathname)s:%(lineno)d"
)

DEV_DEBUG_LOG_FORMAT = (
    "%(asctime)s %(levelname)s - %(message)s - from %(funcName)s() in"
    " %(filename)s:%(lineno)d"
)


# fields named in LOG_FORMAT and LOG_FORMAT_EXTRA_JSON_KEYS
# will always be included in json log output even if
# no such field was supplied in the log record,
# substituting a None value if necessary.
LOG_FORMAT_EXTRA_JSON_KEYS = ()


logger = logging.getLogger(__name__)


def _common_request_extra_log_context():
    return {
        "method": request.method,
        "url": request.url,
        "endpoint": request.endpoint,
        # pid and thread ident are both available on LogRecord by default,
        # as `process` and `thread` respectively, but I don't see a
        # straightforward way of selectively including them only in certain
        # log messages - they are designed to be included when the formatter
        # is being configured. This is why I'm manually grabbing them and
        # putting them in as `extra` here, avoiding the existing parameter
        # names to prevent LogRecord from complaining
        "process_": getpid(),
        # stringifying this as it could potentially be a long that json is
        # unable to represent accurately
        "thread_": str(get_thread_ident()),
    }


def init_app(app):
    app.config.setdefault("FSD_LOG_LEVEL", "INFO")

    @app.before_request
    def before_request():
        # annotating these onto request instead of flask.g as they probably
        # shouldn't be inheritable from a request-less application context
        request.before_request_real_time = time.perf_counter()
        request.before_request_process_time = time.process_time()

        current_app.logger.log(
            logging.DEBUG,
            "Received request {method} {url}",
            extra=_common_request_extra_log_context(),
        )

    @app.after_request
    def after_request(response):
        current_app.logger.log(
            logging.ERROR
            if response.status_code // 100 == 5
            else logging.INFO,
            "{method} {url} {status}",
            extra={
                "status": response.status_code,
                "duration_real": (
                    (time.perf_counter() - request.before_request_real_time)
                    if hasattr(request, "before_request_real_time")
                    else None
                ),
                "duration_process": (
                    (time.process_time() - request.before_request_process_time)
                    if hasattr(request, "before_request_process_time")
                    else None
                ),
                **_common_request_extra_log_context(),
            },
        )
        return response

    logging.getLogger().addHandler(logging.NullHandler())
    # Werkzeug logging
    werkzeug_logger = logging.getLogger("werkzeug")
    # Disable default werkzeug logging
    werkzeug_logger.disabled = True
    # Set default handler to log to stdout
    handlers = [logging.StreamHandler(sys.stdout)]

    # Clear any preset logger handlers
    del app.logger.handlers[:]

    # Switch between text or json log formats
    if app.config.get("FLASK_ENV") == "development":
        formatter = CustomLogFormatter(DEV_DEBUG_LOG_FORMAT)
    else:
        formatter = JSONFormatter(get_json_log_format())

    # Configure handlers
    for handler in handlers:
        configure_handler(handler, app, formatter)

    loglevel = logging.getLevelName(app.config["FSD_LOG_LEVEL"])
    loggers = [app.logger, werkzeug_logger]

    for logger_ in loggers:
        for handler in handlers:
            logger_.addHandler(handler)
        logger_.setLevel(loglevel)
    app.logger.info("Logging configured")


def configure_handler(handler, app, formatter):
    handler.setLevel(logging.getLevelName(app.config["FSD_LOG_LEVEL"]))
    handler.setFormatter(formatter)
    handler.addFilter(RequestExtraContextFilter())
    if os.environ.get("CF_INSTANCE_INDEX"):
        handler.addFilter(AppInstanceFilter())

    return handler


def get_json_log_format():
    return LOG_FORMAT + "".join(
        f" %({key})s" for key in LOG_FORMAT_EXTRA_JSON_KEYS
    )


class AppInstanceFilter(logging.Filter):
    def __init__(self):
        self.instance_index = os.environ["CF_INSTANCE_INDEX"]

    def filter(self, record):
        record.instance_index = self.instance_index

        return record


class BaseExtraStackLocationFilter(logging.Filter):
    def __init__(self, param_prefix):
        self._param_prefix = param_prefix

    def is_interesting_frame(self, frame):
        raise NotImplementedError

    def enabled_for_record(self, record):
        return True

    def _findCaller(self):
        """
        Cut down copy of Python 3.6.6's logging.Logger.findCaller()

        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        f = logging.currentframe()
        if f is not None:
            f = f.f_back
        while hasattr(f, "f_code"):
            co = f.f_code
            try:
                # do this in a try block to protect ourselves from
                # faulty is_interesting_frame implementations
                is_interesting_frame = self.is_interesting_frame(f)
            except:  # noqa
                is_interesting_frame = False
            if is_interesting_frame:
                return co.co_filename, f.f_lineno, co.co_name
            f = f.f_back
        return None, None, None

    def filter(self, record):
        if not self.enabled_for_record(record):
            return record

        rv = self._findCaller()

        if rv != (
            None,
            None,
            None,
        ):
            for attr_name, attr_value in zip(
                (
                    "pathname",
                    "lineno",
                    "funcName",
                ),
                rv,
            ):
                setattr(record, self._param_prefix + attr_name, attr_value)

        return record


class RequestExtraContextFilter(logging.Filter):
    """
    Filter which will pull extra context from
    the current request's `get_extra_log_context` method
    (if present) and make this available on log records
    """

    def filter(self, record):
        if has_request_context() and callable(
            getattr(request, "get_extra_log_context", None)
        ):
            for key, value in request.get_extra_log_context().items():
                setattr(record, key, value)

        return record


class CustomLogFormatter(logging.Formatter):
    """
    Accepts a format string for the message
    and formats it with the extra fields
    with console colouring option
    """

    FORMAT_STRING_FIELDS_PATTERN = re.compile(r"\((.+?)\)")
    GREY = "\x1b[38;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m😠"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"

    COLOURS = {
        "DEBUG": GREY,
        "INFO": GREY,
        "WARNING": YELLOW,
        "ERROR": RED,
        "CRITICAL": BOLD_RED,
    }

    def __init__(self, msg, use_color=True):
        date_strftime_format = "%d-%b-%y %H:%M:%S"
        logging.Formatter.__init__(self, msg, datefmt=date_strftime_format)
        self.use_color = use_color

    def add_fields(self, record):
        """
        Ensure all values found in our `fmt`
        have non-None entries in `record`
        """
        for field in self.FORMAT_STRING_FIELDS_PATTERN.findall(self._fmt):
            # slightly clunky - this is so we catch
            # explicitly-set Nones too and turn them into "-"
            fetched_value = record.__dict__.get(field)
            string_value = fetched_value if fetched_value is not None else "-"
            if self.use_color and field == "levelname":
                string_value = self.colour_field(record, string_value)
            record.__dict__[field] = string_value

    def colour_field(self, record, msg):
        color = self.COLOURS.get(record.levelname)
        return color + msg + self.RESET

    def format(self, record):
        self.add_fields(record)
        msg = super(CustomLogFormatter, self).format(record)

        try:
            msg = msg.format(**record.__dict__)
        except:  # noqa
            # We know that KeyError, ValueError and IndexError are all
            # possible things that can go wrong here - there is no guarantee
            # that the message passed into the logger is actually suitable
            # to be used as a format string. This is particularly so where
            # we are logging arbitrary exception that may reference code.
            #
            # We catch all exceptions rather than just those three, because
            # _any_ failure to format the message must not result in an error,
            # otherwise the original log message will never be returned and
            # written to the logs, and that might be important info such as an
            # exception.
            #
            # NB do not attempt to log either the exception or `msg` here,
            # or you will find that too fails, and you end up with an
            # infinite recursion / stack overflow.
            logger.info("failed to format log message")

        return msg


class JSONFormatter(BaseJSONFormatter):
    def __init__(self, *args, max_missing_key_attempts=5, **kwargs):
        super().__init__(*args, **kwargs)
        self._max_missing_key_attempts = max_missing_key_attempts

    def formatTime(self, record, datefmt: str | None = ...) -> str:
        ct = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            s = (
                datetime.datetime.fromtimestamp(
                    record.created, datetime.timezone.utc
                )
                .astimezone()
                .isoformat(sep=" ", timespec="milliseconds")
            )
        return s

    def process_log_record(self, log_record):
        for key, newkey in (
            (
                "asctime",
                "time",
            ),
            (
                "trace_id",
                "requestId",
            ),
        ):
            try:
                log_record[newkey] = log_record.pop(key)
            except KeyError:
                pass

        log_record["logType"] = "application"

        missing_keys = {}
        for attempt in range(self._max_missing_key_attempts):
            try:
                log_record["message"] = log_record["message"].format(
                    **log_record, **missing_keys
                )
            except KeyError as e:
                missing_keys[e.args[0]] = f"{{{e.args[0]}: missing key}}"
            else:
                # execution should only ever reach this point once
                # - when the .format() succeeds
                if missing_keys:
                    logger.warning(
                        "Missing keys when formatting log message: {}".format(
                            tuple(missing_keys.keys())
                        )
                    )

                break

        else:
            logger.exception(
                "Too many missing keys when attempting to format log message:"
                " gave up"
            )

        return log_record
