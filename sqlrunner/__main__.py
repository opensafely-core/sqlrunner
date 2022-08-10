from main import parse_args, read_sql, run_sql, write_results


def main():
    args = parse_args()
    url = args.url
    sql_query = args.sql_query
    output = args.output

    sql_query = read_sql(sql_query)

    results = run_sql(url=url, sql_query=sql_query)

    write_results(results, output)


if __name__ == "__main__":
    main()
