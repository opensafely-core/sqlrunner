from main import parse_args, read_sql, run_sql, write_results


def main():
    args = parse_args()
    url = args.url
    f_path_input = args.f_path_input
    f_path_output = args.f_path_output
    sql_query = read_sql(f_path_input)

    results = run_sql(url=url, sql_query=sql_query)

    write_results(results, f_path_output)


if __name__ == "__main__":
    main()
