import pathlib

import pymssql

from sqlrunner import main


def test_parse_args(monkeypatch):
    # arrange
    monkeypatch.setattr(
        "sys.argv",
        [
            "main.py",
            "--database_connection",
            "lalala",
            "--sql_query",
            "query.sql",
            "--output",
            "results.csv",
        ],
    )

    # act
    args = main.parse_args()

    # assert
    assert args.database_connection == "lalala"
    assert args.sql_query == pathlib.Path("query.sql")
    assert args.output == pathlib.Path("results.csv")


def test_read_sql(tmp_path):
    # arrange
    sql_file = tmp_path / "query.sql"
    sql_file.write_text("SELECT id FROM my_table;", "utf-8")

    # act
    sql_query = main.read_sql(sql_file)

    # assert
    assert sql_query == "SELECT id FROM my_table;"


def test_write_results(tmp_path):
    # arrange
    results_file = tmp_path / "results.csv"  # noqa
    results = [{"id": 1}, {"id": 2}]  # noqa

    # act
    main.write_results(results, results_file)

    # assert
    # TODO


def test_run_sql(mssql_database):
    # arrange
    # https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls
    # dialect+driver://username:password@host:port/database
    user = mssql_database["username"]
    password = mssql_database["password"]
    port = int(mssql_database["port_from_host"])
    server = mssql_database["host_from_host"]
    database = mssql_database["db_name"]
    # try:
    conn = pymssql.connect(
        user=user, server=server, password=password, database=database, port=port
    )
    cursor = conn.cursor()
    cursor.execute("SELECT 123")
    # assert
    assert cursor.fetchall() == [(123,)]
    conn.close()
