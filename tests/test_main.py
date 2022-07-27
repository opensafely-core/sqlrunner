def test_parse_args(monkeypatch):
    # arrange
    monkeypatch.setattr(
        "sys.argv",
        [
            "__main__.py",
            "--database_connection",
            "",
            "--sql_query",
            "",
            "--output",
            "",
        ],
    )

    # act
    # ...

    # assert
    # ...


def test_read_sql(tmp_path):
    # arrange
    sql_file = tmp_path / "query.sql"
    sql_file.write_text("SELECT id FROM my_table;", "utf-8")

    # act
    # ...

    # assert
    # ...


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
