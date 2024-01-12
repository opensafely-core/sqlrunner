import csv
import gzip
import itertools
import pathlib
import sys
from urllib import parse

import pymssql
import structlog
from sqlglot.dialects import TSQL
from sqlglot.optimizer.qualify_columns import qualify_columns

from sqlrunner import T1OOS_TABLE, utils

from .mssql_log_utils import execute_with_log


log = structlog.get_logger()


def main(args):
    sql_query = read_text(args["input"])
    if not are_t1oos_handled(sql_query):
        raise RuntimeError("T1OOs are not handled correctly")

    if args["dsn"] is None:
        # Bypass the database
        if args["dummy_data_file"] is None:
            results = iter([{x: None for x in get_column_headers(sql_query)}])
        else:
            results = read_dummy_data_file(args["dummy_data_file"])
    else:
        results = run_sql(
            dsn=args["dsn"],
            sql_query=sql_query,
            include_statistics=args["include_statistics"],
        )

    output = args["output"] or sys.stdout
    write_results(results, output)


def get_column_headers(sql_query):
    tsql_parser = TSQL()

    # filter out any empty expressions returned by parser
    parsed = [q for q in tsql_parser.parse(sql_query) if q is not None]

    # expand out "*" to full column names if referencing another object
    # in query with explicit column names
    columns = qualify_columns(parsed[-1], schema=None, infer_schema=True).named_selects

    # if "*" not referencing an object with explicit column names
    # we don't know what the headers should be
    if "*" in columns:
        raise RuntimeError(
            "Headers can only be generated for queries with explicit column names"
        )

    return columns


def read_text(f_path):
    return f_path.read_text(encoding="utf-8")


def are_t1oos_handled(sql_query):
    return sql_query.find(T1OOS_TABLE) >= 0


def parse_dsn(dsn):
    parse_result = parse.urlparse(dsn)
    return {
        "user": parse.unquote(parse_result.username),
        "password": parse.unquote(parse_result.password),
        "server": parse_result.hostname,
        "port": parse_result.port or 1433,
        "database": parse_result.path.strip("/"),
    }


def run_sql(*, dsn, sql_query, include_statistics=False):
    # `dsn` is expected to follow RFC-1738, just as SQL Alchemy expects:
    # <https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls>
    # dialect+driver://username:password@host:port/database
    parsed_dsn = parse_dsn(dsn)
    conn = pymssql.connect(**parsed_dsn, as_dict=True)
    cursor = conn.cursor()
    log.info("start_executing_sql_query")
    if include_statistics:
        execute_with_log(cursor, sql_query, log)
    else:
        cursor.execute(sql_query)
    log.info("finish_executing_sql_query")
    yield from cursor
    conn.close()


def write_results(results, destination):
    dest_is_path = isinstance(destination, pathlib.Path)

    if dest_is_path:
        # If writing to file, job-runner expects the output CSV file to exist.
        # If it doesn't, then the SQL Runner action will fail.
        # A user won't know whether their query returns any results,
        # so to avoid the SQL Runner action failing,
        # we write an empty output CSV file.
        utils.touch(destination)

        if destination.suffixes == [".csv", ".gz"]:
            destination = gzip.open(
                destination, "wt", newline="", encoding="utf-8", compresslevel=6
            )
        else:
            destination = destination.open(mode="w", newline="", encoding="utf-8")

    try:
        first_result = next(results)
    except StopIteration:
        return

    fieldnames = first_result.keys()

    try:
        writer = csv.DictWriter(destination, fieldnames)
        log.info("start_writing_results")
        writer.writeheader()
        writer.writerows(itertools.chain([first_result], results))
        log.info("finish_writing_results")
    finally:
        if dest_is_path:
            destination.close()


def read_dummy_data_file(f_path):
    with f_path.open("r", newline="") as f:
        yield from csv.DictReader(f)
