from main import parse_args, read_sql, run_sql, write_results


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
