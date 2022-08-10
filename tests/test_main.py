import csv
import pathlib

from sqlrunner import main


def test_parse_args(monkeypatch):
    # arrange
    monkeypatch.setattr(
        "sys.argv",
        [
            "main.py",
            "--url",
            "dialect+driver://user:password@server:port/database",
            "--sql_query",
            "query.sql",
            "--output",
            "results.csv",
        ],
    )

    # act
    args = main.parse_args()

    # assert
    assert args.url == "dialect+driver://user:password@server:port/database"
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
    results_file = tmp_path / "results.csv"

    # act
    main.write_results([{"id": 1}, {"id": 2}], results_file)

    # assert
    with results_file.open(newline="") as f:
        results = list(csv.DictReader(f))

    assert len(results) == 2
    assert results[0] == {"id": "1"}
    assert results[1] == {"id": "2"}


def test_run_sql(mssql_database):
    # arrange
    dialect = "mssql"
    driver = "pymssql"

    user = mssql_database["username"]
    password = mssql_database["password"]
    server = mssql_database["host_from_host"]
    port = mssql_database["port_from_host"]
    database = mssql_database["db_name"]

    # act
    url = f"{dialect}+{driver}://{user}:{password}@{server}:{port}/{database}"
    results = main.run_sql(url=url, sql_query="SELECT 1 AS patient_id")

    # assert
    assert results == [{"patient_id": 1}]
