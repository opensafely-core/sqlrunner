import pathlib

import pytest

from sqlrunner import main


def test_parse_args():
    # act
    args = main.parse_args(
        [
            "--dsn",
            "dialect+driver://user:password@server:port/database",
            "--output",
            "results.csv",
            "query.sql",
        ]
    )

    # assert
    assert args.dsn == "dialect+driver://user:password@server:port/database"
    assert args.input == pathlib.Path("query.sql")
    assert args.output == pathlib.Path("results.csv")
    assert args.dummy_data_file is None


def test_parse_args_with_defaults_from_environ(monkeypatch):
    # act
    args = main.parse_args(
        ["--output", "results.csv", "query.sql"],
        {"DATABASE_URL": "dialect+driver://user:password@server:port/database"},
    )

    # assert
    assert args.dsn == "dialect+driver://user:password@server:port/database"
    assert args.input == pathlib.Path("query.sql")
    assert args.output == pathlib.Path("results.csv")
    assert args.dummy_data_file is None


def test_read_text(tmp_path):
    # arrange
    f_path = tmp_path / "query.sql"
    f_path.write_text("SELECT 1 AS patient_id", "utf-8")

    # act
    sql_query = main.read_text(f_path)

    # assert
    assert sql_query == "SELECT 1 AS patient_id"


@pytest.mark.parametrize(
    "dsn,port",
    [
        ("dialect+driver://username:password@host/database", 1433),
        ("dialect+driver://username:password@host:50161/database", 50161),
    ],
)
def test_parse_dsn(dsn, port):
    parsed_dsn = main.parse_dsn(dsn)
    assert parsed_dsn["port"] == port


def test_run_sql(mssql_database):
    # arrange
    dialect = "mssql"
    driver = "pymssql"
    user = mssql_database["username"]
    password = mssql_database["password"]
    server = mssql_database["host_from_host"]
    port = mssql_database["port_from_host"]
    database = mssql_database["db_name"]
    dsn = f"{dialect}+{driver}://{user}:{password}@{server}:{port}/{database}"

    # act
    results = main.run_sql(dsn=dsn, sql_query="SELECT 1 AS patient_id")

    # assert
    assert results == [{"patient_id": 1}]


def test_write_results(tmp_path):
    # arrange
    f_path = tmp_path / "results.csv"

    # act
    main.write_results([{"id": 1}, {"id": 2}], f_path)

    # assert
    assert f_path.read_text(encoding="utf-8") == "id\n1\n2\n"


@pytest.mark.parametrize(
    "dummy_data_fname,results_fname",
    [
        ("results.csv", "results.csv"),
        ("dummy_data_file.csv", "results.csv"),
    ],
)
def test_write_results_from_dummy_data_file(dummy_data_fname, results_fname, tmp_path):
    # arrange
    dummy_data_file = tmp_path / dummy_data_fname
    dummy_data_file.write_text("id\n1\n2\n", encoding="utf-8")
    results_file = tmp_path / results_fname

    # act
    main.write_results(dummy_data_file, results_file)

    # assert
    assert results_file.read_text(encoding="utf-8") == "id\n1\n2\n"
