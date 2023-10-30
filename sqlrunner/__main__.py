import logging
import os
import sys

import structlog

from sqlrunner import main


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


def entrypoint():
    args = main.parse_args(sys.argv[1:], os.environ)

    handlers = [logging.StreamHandler(sys.stdout)]
    # This is covered indirectly by a test.
    if args.log_file is not None:  # pragma: no cover
        handlers.append(logging.FileHandler(args.log_file, "w"))
    logging.basicConfig(format="%(message)s", level=logging.INFO, handlers=handlers)

    if args.dsn is None and args.dummy_data_file is not None:
        # Bypass the database
        results = args.dummy_data_file
    else:
        sql_query = main.read_text(args.input)
        results = main.run_sql(dsn=args.dsn, sql_query=sql_query)
    main.write_results(results, args.output)


if __name__ == "__main__":
    entrypoint()  # pragma: no cover
