import argparse
import csv
import pathlib
from urllib import parse

import pymssql


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        required=True,
        type=str,
        help="String of database connection",
    )
    parser.add_argument(
        "--sql_query",
        required=True,
        type=pathlib.Path,
        help="Path to the SQL file containing the query",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=pathlib.Path,
        help="Path to the output CSV file",
    )
    return parser.parse_args()


def read_sql(sql_query):
    return sql_query.read_text(encoding="utf-8")


def run_sql(url, sql_query):
    parsed_url = parse.urlparse(url)

    conn = pymssql.connect(
        user=parsed_url.username,
        password=parsed_url.password,
        server=parsed_url.hostname,
        port=parsed_url.port,
        database=parsed_url.path[1:],
        as_dict=True,
    )
    cursor = conn.cursor()
    cursor.execute(sql_query)
    results = cursor.fetchall()
    conn.close()

    return results


def write_results(results, path):
    with path.open(mode="w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
