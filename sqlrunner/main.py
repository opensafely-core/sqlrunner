import contextlib
import csv
import gzip
import itertools
import re
import sys
from urllib import parse

import pymssql
import structlog
from sqlglot.dialects import TSQL
from sqlglot.optimizer.qualify_columns import qualify_columns

from sqlrunner import OLD_T1OOS_TABLE, T1OOS_TABLE, utils


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
        results = run_sql(dsn=args["dsn"], sql_query=sql_query)
    write_results(results, args["output"])


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
    if re.search(rf"\b{T1OOS_TABLE}", sql_query):
        # If T1OOS_TABLE is referenced in the query, then the query is safe to run.
        # The word boundary (\b) is necessary because PatientsWithTypeOneDissent
        # is a substring of AllowedPatientsWithTypeOneDissent.
        return True
    if re.search(f"--.*{OLD_T1OOS_TABLE}", sql_query):
        # If OLD_T1OOS_TABLE is referenced in a comment in the query, then the query
        # is safe to run.  (It would be unnecessary faff to change existing queries
        # that reference the old table namein a comment to explain why T1OO data
        # haven't been excluded.)
        return True
    return False


def parse_dsn(dsn):
    parse_result = parse.urlparse(dsn)
    return {
        "user": parse.unquote(parse_result.username),
        "password": parse.unquote(parse_result.password),
        "server": parse_result.hostname,
        "port": parse_result.port or 1433,
        "database": parse_result.path.strip("/"),
    }


def run_sql(*, dsn, sql_query):
    # `dsn` is expected to follow RFC-1738, just as SQL Alchemy expects:
    # <https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls>
    # dialect+driver://username:password@host:port/database
    parsed_dsn = parse_dsn(dsn)
    conn = pymssql.connect(**parsed_dsn, as_dict=True)
    cursor = conn.cursor()
    log.info("start_executing_sql_query")
    cursor.execute(sql_query)
    log.info("finish_executing_sql_query")
    yield from cursor
    conn.close()


def write_results(results, f_path):
    if f_path is not None:
        # job-runner expects the output CSV file to exist. If it doesn't, then the SQL
        # Runner action will fail. A user won't know whether their query returns any
        # results, so to avoid the SQL Runner action failing, we write an empty output
        # CSV file.
        utils.touch(f_path)

    try:
        first_result = next(results)
    except StopIteration:
        return

    fieldnames = first_result.keys()

    if f_path is not None:
        kwargs = {"newline": "", "encoding": "utf-8"}
        if f_path.suffixes == [".csv", ".gz"]:
            context = gzip.open(f_path, "wt", compresslevel=6, **kwargs)
        else:
            context = open(f_path, "w", **kwargs)
    else:
        context = contextlib.nullcontext(sys.stdout)

    with context as f:
        writer = csv.DictWriter(f, fieldnames)
        log.info("start_writing_results")
        writer.writeheader()
        writer.writerows(itertools.chain([first_result], results))
        log.info("finish_writing_results")


def read_dummy_data_file(f_path):
    kwargs = {"newline": "", "encoding": "utf-8"}
    if f_path.suffixes == [".csv", ".gz"]:
        context = gzip.open(f_path, "rt", **kwargs)
    else:
        context = open(f_path, **kwargs)

    with context as f:
        yield from csv.DictReader(f)
