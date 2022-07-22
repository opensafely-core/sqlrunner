import argparse
import pathlib


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--database_connection",
        required=True,
        type=str,
        help="String of database connection",
    )
    parser.add_argument(
        "--input_file",
        required=True,
        type=pathlib.Path,
        help="Path to the input SQL file",
    )
    parser.add_argument(
        "--output_file",
        required=True,
        type=pathlib.Path,
        help="Path to the output CSV file",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    database_connection = args.database_connection
    input_file = args.input_file
    output_file = args.output_file
    print(database_connection, input_file, output_file)


if __name__ == "__main__":
    main()
