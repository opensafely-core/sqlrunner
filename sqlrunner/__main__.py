import argparse
import csv
import pathlib

from main import run_sql


def parse_args():
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
    """Open and read SQL file"""
    return sql_query.read_text(encoding="utf-8")


def write_results(results, path):
    """Write results"""
    with path.open(mode="w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)


def main():
    # Parse arguments
    args = parse_args()
    database_connection = args.database_connection
    sql_query = args.sql_query
    output = args.output

    sql_query = read_sql(sql_query)

    # Run SQL
    results = run_sql(database_connection=database_connection, sql_query=sql_query)

    # Write CSV file (here just print all arguments for now)
    write_results(results, output)


if __name__ == "__main__":
    main()
