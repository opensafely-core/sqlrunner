import sys

from sqlrunner import main


args = main.parse_args(sys.argv[1:])
sql_query = main.read_text(args.input)
results = main.run_sql(dsn=args.dsn, sql_query=sql_query)
main.write_results(results, args.output)
