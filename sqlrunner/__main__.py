from sqlrunner import main


args = main.parse_args()
url = args.url
input_file = args.input_file
output_file = args.output_file

sql_query = main.read_text(input_file)
results = main.run_sql(url=url, sql_query=sql_query)

main.write_results(results, output_file)
