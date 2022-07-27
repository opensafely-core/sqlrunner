import pathlib

from sqlrunner import main


def test_parse_args(monkeypatch):
    # arrange
    monkeypatch.setattr(
        "sys.argv",
        [
            "main.py",
            "--database_connection",
            "",
            "--sql_query",
            "",
            "--output",
            "",
        ],
    )

    # act
    args = main.parse_args()

    # assert
    assert args.database_connection == ""
    assert args.sql_query == pathlib.Path("")
    assert args.output == pathlib.Path("")


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
    # ...

    # assert
    # ...


def test_run_sql(mssql_database):
    # https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls
    # dialect+driver://username:password@host:port/database
    pass
