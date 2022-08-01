import csv
import pathlib

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

    with results_file.open(mode="r", newline="", encoding="utf-8") as csv_file:
        results = csv.reader(csv_file)
        for row in results:
            print(", ".join(row))

    # assert
    # TODO: This needs a better test
    assert row == ["2"]


def test_run_sql(mssql_database):
    # arrange

    # act
    main.run_sql(database_connection=mssql_database, sql_query="SELECT 123")

    # assert
