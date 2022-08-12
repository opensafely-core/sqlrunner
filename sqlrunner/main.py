import argparse
import csv
import pathlib
from urllib import parse

import pymssql


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dsn",
        required=True,
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
    return parser.parse_args()


def read_text(f_path):
    return f_path.read_text(encoding="utf-8")


def run_sql(*, dsn, sql_query):
    # `dsn` is expected to follow RFC-1738, just as SQL Alchemy expects:
    # <https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls>
    # dialect+driver://username:password@host:port/database
    parsed_dsn = parse.urlparse(dsn)

    conn = pymssql.connect(
        user=parsed_dsn.username,
        password=parsed_dsn.password,
        server=parsed_dsn.hostname,
        port=parsed_dsn.port,
        database=parsed_dsn.path.strip("/"),
        as_dict=True,
    )
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
