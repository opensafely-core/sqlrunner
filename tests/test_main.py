import functools
import gzip

import pytest

from sqlrunner import T1OOS_TABLE, main


def test_main_with_t1oos_not_handled(tmp_path):
    input_ = tmp_path / "query.sql"
    input_.write_text("SELECT Patient_ID FROM Patient", "utf-8")
    with pytest.raises(RuntimeError):
        main.main({"input": input_})


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
                WHERE Patient_ID IN (SELECT Patient_ID FROM {T1OOS_TABLE})
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
                SELECT Patient_ID FROM Patient
                WHERE Patient_ID NOT IN (SELECT Patient_ID FROM {T1OOS_TABLE})
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
    "context,suffix",
    [
        (functools.partial(open, mode="w"), ".csv"),
        (functools.partial(gzip.open, mode="wt"), ".csv.gz"),
    ],
)
def test_read_dummy_data_file(context, suffix, tmp_path):
    dummy_data_file = tmp_path / f"dummy_data_file{suffix}"
    with context(dummy_data_file, encoding="utf-8", newline="") as f:
        f.writelines(["id\n", "1\n", "2\n"])

    dummy_rows = list(main.read_dummy_data_file(dummy_data_file))
    assert dummy_rows == [{"id": "1"}, {"id": "2"}]


@pytest.mark.parametrize(
    "sql_query",
    [
        # A complex query with a common table expression and a correlated
        # subquery and column aliases to ensure that the parser
        # correctly identifies the output columns
        """
        ;with CTE as (
        SELECT
            column1,
            [column 2],
            count(*) as column_3
        FROM
            table
        GROUP BY
            column1,
            [column 2],
        )
        SELECT c.*,x.column_4
        FROM CTE c
        JOIN (
            SELECT
                column1,
                column_4
            FROM table2
        ) x
            ON c.column1 = x.column1
        """,
        # A multi-statement batch to ensure we create headers for the last
        # statement in the batch
        """
        SELECT foo, bar, baz, qux
        INTO #temptable;
        SELECT
            foo as [column1],
            bar as [column 2],
            baz as [column_3],
            qux as [column_4]
        FROM #temptable
        """,
    ],
)
def test_generate_column_headers(sql_query):
    assert main.get_column_headers(sql_query) == [
        "column1",
        "column 2",
        "column_3",
        "column_4",
    ]


def test_generate_column_headers_fails_on_select_star():
    # Ensure that a helpful error message is generated
    # if a user tries to generate columns from a query
    # that has `*` in the select list
    with pytest.raises(
        RuntimeError,
        match=r"Headers can only be generated for queries with explicit column names",
    ):
        main.get_column_headers("SELECT * FROM table")
