import argparse
import pathlib

import run_sql


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--database_connection",
        required=True,
        type=str,
        help="String of database connection",
    )
    parser.add_argument(
        "--input_sql_file",
        required=True,
        type=pathlib.Path,
        help="Path to the input SQL file",
    )
    parser.add_argument(
        "--output_csv_file",
        required=True,
        type=pathlib.Path,
        help="Path to the output CSV file",
    )
    return parser.parse_args()


def main():
    # Parse arguments
    args = parse_args()
    database_connection = args.database_connection
    input_sql_file = args.input_sql_file
    output_csv_file = args.output_csv_file

    # Run SQL
    output = run_sql.run_sql(
        database_connection=database_connection, input_sql_file=input_sql_file
    )

    # Write CSV file (here just print all arguments for now)
    print(output, output_csv_file)


if __name__ == "__main__":
    main()
