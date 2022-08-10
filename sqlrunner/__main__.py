from sqlrunner import main


args = main.parse_args()
sql_query = main.read_text(args.input_file)
results = main.run_sql(url=args.url, sql_query=sql_query)
main.write_results(results, args.output_file)
