import gzip

import pytest

from sqlrunner import T1OOS_TABLE, main


def test_main_with_t1oos_not_handled(tmp_path):
    input_ = tmp_path / "query.sql"
    input_.write_text("SELECT Patient_ID FROM Patient", "utf-8")
    with pytest.raises(RuntimeError):
        main.main({"input": input_})


def test_main_with_dummy_data_file(tmp_path):
    input_ = tmp_path / "query.sql"
    input_.write_text(
        f"-- {T1OOS_TABLE} intentionally not excluded\nSELECT Patient_ID FROM Patient",
        "utf-8",
    )
    dummy_data_file = tmp_path / "dummy_data.csv"
    dummy_data_file.write_text("patient_id\n1\n", "utf-8")
    output = tmp_path / "results.csv"
    main.main(
        {
            "dsn": None,
            "input": input_,
            "dummy_data_file": dummy_data_file,
            "output": output,
        }
    )
    assert output.read_text("utf-8") == "patient_id\n1\n"


@pytest.mark.parametrize(
    "sql_query,are_t1oos_handled",
    [
        # not handled by query
        (
            """
                SELECT Patient_ID FROM Patient
            """,
            False,
        ),
        # handled by query
        (
            f"""
                SELECT Patient_ID FROM Patient
                WHERE Patient_ID NOT IN (SELECT Patient_ID FROM {T1OOS_TABLE})
            """,
            True,
        ),
        # not handled by comment
        (
            """
                -- t100s intentionally not excluded
                SELECT Patient_ID FROM Patient
            """,
            False,
        ),
        # handled by comment
        (
            f"""
                -- {T1OOS_TABLE} intentionally not excluded
                SELECT Patient_ID FROM Patient
            """,
            True,
        ),
        # handled by query, but undesirable: it's hard to prevent this with a "light
        # touch" approach
        (
            f"""
                SELECT Patient_ID FROM {T1OOS_TABLE}
             """,
            True,
        ),
    ],
)
def test_are_t1oos_handled(sql_query, are_t1oos_handled):
    assert main.are_t1oos_handled(sql_query) == are_t1oos_handled


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


def test_run_sql(dsn, log_output):
    sql_query = "SELECT 1 AS patient_id"
    results = main.run_sql(dsn=dsn, sql_query=sql_query)
    assert list(results) == [{"patient_id": 1}]
    assert log_output.entries == [
        {"event": "start_executing_sql_query", "log_level": "info"},
        {"event": "finish_executing_sql_query", "log_level": "info"},
    ]


@pytest.fixture(params=[None, "subdir"])
def output_path(tmp_path, request):
    """Returns a temporary output path object.

    This fixture helps us to test two cases. Namely, when SQL Runner writes:
    to the default output directory, which is usually checked-in and so usually exists;
    to a sub-directory of the default output directory, which isn't usually checked-in
    and so doesn't usually exist.
    """
    return tmp_path if request.param is None else tmp_path / request.param


def test_write_zero_results(output_path):
    f_path = output_path / "results.csv"
    main.write_results(iter([]), f_path)
    assert f_path.read_text(encoding="utf-8") == ""


def test_write_results_uncompressed(output_path, log_output):
    f_path = output_path / "results.csv"
    main.write_results(iter([{"id": 1}, {"id": 2}]), f_path)
    assert f_path.read_text(encoding="utf-8") == "id\n1\n2\n"
    assert log_output.entries == [
        {"event": "start_writing_results", "log_level": "info"},
        {"event": "finish_writing_results", "log_level": "info"},
    ]


def test_write_results_compressed(output_path):
    f_path = output_path / "results.csv.gz"
    results = [{"id": 1}, {"id": 2}]
    main.write_results(iter(results), f_path)
    assert gzip.open(f_path, "rt").read() == "id\n1\n2\n"


@pytest.mark.parametrize(
    "dummy_data_fname,results_fname",
    [
        ("results.csv", "results.csv"),
        ("dummy_data_file.csv", "results.csv"),
        ("results.csv", "subdir/results.csv"),
    ],
)
def test_write_results_from_dummy_data_file(dummy_data_fname, results_fname, tmp_path):
    dummy_data_file = tmp_path / dummy_data_fname
    dummy_data_file.write_text("id\n1\n2\n", encoding="utf-8")
    results_file = tmp_path / results_fname
    main.write_results(dummy_data_file, results_file)
    assert results_file.read_text(encoding="utf-8") == "id\n1\n2\n"
