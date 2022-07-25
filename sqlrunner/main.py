# import pymssql


def run_sql(database_connection, sql_query):
    """
    Run arbitrary SQL code against an OpenSAFELY backend
    """

    # 1. create a connection from the given URL
    # Check PyMySQL examples
    # https://pypi.org/project/pymssql/#basic-example
    # https://pymssql.readthedocs.io/en/stable/pymssql_examples.html

    # 2. Read the SQL code from the given path

    # 3. Execute the SQL against the connection

    # 4. Write the output to a CSV file
    # Use pattern of basic example in the docs:
    # https://pypi.org/project/pymssql/#basic-example

    return [
        {"event_code": 1, "event_desc": "event 1 description", "count": 1},
        {"event_code": 2, "event_desc": "event 2 description", "count": 5},
        {"event_code": 3, "event_desc": "event 3 description", "count": 10},
    ]
