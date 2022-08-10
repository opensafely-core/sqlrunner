from main import parse_args, read_text, run_sql, write_results


def main():
    args = parse_args()
    url = args.url
    input_file = args.input_file
    output_file = args.output_file

    sql_query = read_text(input_file)
    results = run_sql(url=url, sql_query=sql_query)

    write_results(results, output_file)


if __name__ == "__main__":
    main()
