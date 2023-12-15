import argparse
import logging
import os
import pathlib
import sys

import structlog

from sqlrunner import __version__, main, utils


# Configure structlog to output structured logs in JSON format. For more information,
# see:
# https://www.structlog.org/en/stable/standard-library.html#rendering-within-structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            }
        ),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
)


def parse_args(args, environ):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dsn",
        default=environ.get("DATABASE_URL"),
        help="Data Source Name",
    )
    parser.add_argument(
        "input",
        type=pathlib.Path,
        help="Path to the input SQL file",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=pathlib.Path,
        help="Path to the output CSV file",
    )
    parser.add_argument(
        "--dummy-data-file",
        type=pathlib.Path,
        help="Path to the input dummy data file to be used as the output CSV file",
    )
    parser.add_argument(
        "--log-file",
        type=pathlib.Path,
        help="Path to the log file",
    )
    parser.add_argument(
        "--version", action="version", version=f"sqlrunner {__version__}"
    )
    parser.add_argument(
        "--include-statistics",
        action="store_true",
    )
    return vars(parser.parse_args(args))


def entrypoint():
    args = parse_args(sys.argv[1:], os.environ)
    if args["dsn"] is None and args["dummy_data_file"] is None:
        raise RuntimeError("Neither --dsn nor --dummy-data-file were supplied")

    handlers = [logging.StreamHandler(sys.stdout)]
    # This is covered indirectly by a test.
    if args["log_file"] is not None:  # pragma: no cover
        log_file = args["log_file"]
        utils.touch(log_file)
        handlers.append(logging.FileHandler(log_file, "w"))
    logging.basicConfig(format="%(message)s", level=logging.INFO, handlers=handlers)

    main.main(args)


if __name__ == "__main__":
    entrypoint()  # pragma: no cover
