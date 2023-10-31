import argparse
import logging
import os
import pathlib
import sys

import structlog

from sqlrunner import __version__, main


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
    return vars(parser.parse_args(args))


def entrypoint():
    args = parse_args(sys.argv[1:], os.environ)

    handlers = [logging.StreamHandler(sys.stdout)]
    # This is covered indirectly by a test.
    if args["log_file"] is not None:  # pragma: no cover
        handlers.append(logging.FileHandler(args["log_file"], "w"))
    logging.basicConfig(format="%(message)s", level=logging.INFO, handlers=handlers)

    main.main(args)


if __name__ == "__main__":
    entrypoint()  # pragma: no cover
