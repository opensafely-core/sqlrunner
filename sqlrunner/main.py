import argparse
import csv
import pathlib
from urllib import parse

import pymssql

from sqlrunner import __version__


def parse_args(args, environ=None):
    environ = environ or {}
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
        "--version", action="version", version=f"sqlrunner {__version__}"
    )
    return parser.parse_args(args)


def read_text(f_path):
    return f_path.read_text(encoding="utf-8")


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
    cursor.execute(sql_query)
    results = cursor.fetchall()
    conn.close()

    return results


def write_results(results, f_path):
    fieldnames = results[0].keys()
    with f_path.open(mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames)
        writer.writeheader()
        writer.writerows(results)
