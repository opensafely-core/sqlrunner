# import pymssql
import argparse
import csv
import pathlib

import pymssql


def parse_args():
    """Parse arguments that specify database connection and paths to SQL query and output file.

    Returns:
        A dictionary with ...
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
    """Open and read file with SQL code."""
    return sql_query.read_text(encoding="utf-8")


def write_results(results, path):
    """Write results as CSV file including column names."""
    with path.open(mode="w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)


def run_sql(database_connection, sql_query):
    """
    Run arbitrary SQL code against an OpenSAFELY backend.
    """

    server = database_connection
    user = ""
    password = ""
    database = ""
    conn = pymssql.connect(server, user, password, database)
    cursor = conn.cursor()
    cursor.execute(sql_query)
    # 1. create a connection from the given URL
    # Check PyMySQL examples
    # https://pypi.org/project/pymssql/#basic-example
    # https://pymssql.readthedocs.io/en/stable/pymssql_examples.html

    # 2. Read the SQL code from the given path

    # 3. Execute the SQL against the connection

    # 4. Write the output to a CSV file
    # Use pattern of basic example in the docs:
    # https://pypi.org/project/pymssql/#basic-example

    return [
        {"event_code": 1, "event_desc": "event 1 description", "count": 1},
        {"event_code": 2, "event_desc": "event 2 description", "count": 5},
        {"event_code": 3, "event_desc": "event 3 description", "count": 10},
    ]
