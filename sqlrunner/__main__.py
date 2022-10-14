import os
import sys

from sqlrunner import main


args = main.parse_args(sys.argv[1:], os.environ)
sql_query = main.read_text(args.input)
if args.dummy_data_file is None:
    results = main.run_sql(dsn=args.dsn, sql_query=sql_query)
else:
    results = args.dummy_data_file
main.write_results(results, args.output)
