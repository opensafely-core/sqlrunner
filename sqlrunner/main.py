import argparse
import csv
import pathlib
from urllib import parse

import pymssql


def parse_args():
    """Parse arguments that specify database connection and paths to SQL query and output file.

    Returns:
        TODO
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--database_connection",
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
    """Open and read file with SQL code.

    Returns:
        TODO
    """
    return sql_query.read_text(encoding="utf-8")


def run_sql(database_connection, sql_query):
    """
    Run arbitrary SQL code against an OpenSAFELY backend.

    Returns:
        TODO
    """

    parsed_url = parse.urlparse(database_connection)

    conn = pymssql.connect(
        user=parsed_url.username,
        password=parsed_url.password,
        server=parsed_url.hostname,
        port=parsed_url.port,
        database=parsed_url.path,
    )
    cursor = conn.cursor()
    results = cursor.execute(sql_query)
    conn.close()

    return results


def write_results(results, path):
    """Write results as CSV file including column names.
    Returns:
        TODO
    """
    with path.open(mode="w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
