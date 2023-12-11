import csv
import functools
import gzip
import itertools
import pathlib
import shutil
from urllib import parse

import pymssql
import structlog

from sqlrunner import T1OOS_TABLE

from .mssql_log_utils import logging_cursor


log = structlog.get_logger()


def main(args):
    sql_query = read_text(args["input"])
    if not are_t1oos_handled(sql_query):
        raise RuntimeError("T1OOs are not handled correctly")

    if args["dsn"] is None and args["dummy_data_file"] is not None:
        # Bypass the database
        results = args["dummy_data_file"]
    else:
        results = run_sql(
            dsn=args["dsn"],
            sql_query=sql_query,
            include_statistics=args["include_statistics"],
        )
    write_results(results, args["output"])


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
    #    cursor = conn.cursor()

    log.info("start_executing_sql_query")
    with logging_cursor(conn, sql_query, log if include_statistics else None) as cursor:
        cursor.execute(sql_query)
        log.info("finish_executing_sql_query")
        yield from cursor
    conn.close()


def touch(f_path):
    f_path.parent.mkdir(parents=True, exist_ok=True)
    f_path.touch()


@functools.singledispatch
def write_results(results, f_path):
    # job-runner expects the output CSV file to exist. If it doesn't, then the SQL
    # Runner action will fail. A user won't know whether their query returns any
    # results, so to avoid the SQL Runner action failing, we write an empty output CSV
    # file.
    touch(f_path)

    try:
        first_result = next(results)
    except StopIteration:
        return

    fieldnames = first_result.keys()

    if f_path.suffixes == [".csv", ".gz"]:
        f = gzip.open(f_path, "wt", newline="", encoding="utf-8", compresslevel=6)
    else:
        f = f_path.open(mode="w", newline="", encoding="utf-8")

    try:
        writer = csv.DictWriter(f, fieldnames)
        log.info("start_writing_results")
        writer.writeheader()
        writer.writerows(itertools.chain([first_result], results))
        log.info("finish_writing_results")
    finally:
        f.close()


@write_results.register
def _(results: pathlib.Path, f_path):
    if f_path.exists() and f_path.samefile(results):
        return

    touch(f_path)
    shutil.copy(results, f_path)
