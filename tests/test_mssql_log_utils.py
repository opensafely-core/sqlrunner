import pytest

from sqlrunner.mssql_log_utils import (
    parse_statistics_messages,
)


@pytest.mark.parametrize(
    "messages,results",
    [
        (
            [
                b"This message will not be parseable and should be ignored",
                (
                    b"SQL Server parse and compile time: \n"
                    b"   CPU time = 10 ms, elapsed time = 5 ms."
                ),
                (
                    b"\n SQL Server Execution Times:\n"
                    b"   CPU time = 100 ms,  elapsed time = 0 ms."
                ),
                (
                    b"SQL Server parse and compile time: \n"
                    b"   CPU time = 50 ms, elapsed time = 16 ms."
                ),
                (
                    b"\n SQL Server Execution Times:\n"
                    b"   CPU time = 123 ms,  elapsed time = 456 ms."
                ),
                (
                    b"Table 'Workfile'. Scan count 1, logical reads 2, physical reads 3,"
                    b" read-ahead reads 4, lob logical reads 5, lob physical reads 6,"
                    b" lob read-ahead reads 7."
                ),
                (
                    b"Table 'Worktable'. Scan count 0, logical reads 0, physical reads 0,"
                    b" read-ahead reads 0, lob logical reads 0, lob physical reads 0,"
                    b" lob read-ahead reads 0."
                ),
                (
                    b"Table '#inline_data_1______________________________________________________________________________________________________00000000149B'."
                    b" Scan count 1, logical reads 7, physical reads 0, read-ahead reads 0,"
                    b" lob logical reads 0, lob physical reads 0, lob read-ahead reads 0."
                ),
                (
                    b"Table '#tmp_1______________________________________________________________________________________________________________0000000014D9'."
                    b" Scan count 1, logical reads 4, physical reads 0, read-ahead reads 0,"
                    b" lob logical reads 0, lob physical reads 0, lob read-ahead reads 0."
                ),
                (
                    b"Table '#tmp_1______________________________________________________________________________________________________________0000000014B1'."
                    b" Scan count 1, logical reads 0, physical reads 0, read-ahead reads 0,"
                    b" lob logical reads 0, lob physical reads 0, lob read-ahead reads 0."
                ),
                (
                    b"Table '#tmp_1______________________________________________________________________________________________________________000000001517'."
                    b" Scan count 1, logical reads 0, physical reads 0, read-ahead reads 0, "
                    b"lob logical reads 0, lob physical reads 0, lob read-ahead reads 0."
                ),
            ],
            {
                "timings": {
                    "exec_cpu_ms": 223,
                    "exec_elapsed_ms": 456,
                    "exec_cpu_ratio": 0.49,
                    "parse_cpu_ms": 60,
                    "parse_elapsed_ms": 21,
                },
                "table_io": {
                    "Workfile": {
                        "lob_logical": 5,
                        "lob_physical": 6,
                        "lob_read_ahead": 7,
                        "logical": 2,
                        "physical": 3,
                        "read_ahead": 4,
                        "scans": 1,
                    },
                    "Worktable": {
                        "lob_logical": 0,
                        "lob_physical": 0,
                        "lob_read_ahead": 0,
                        "logical": 0,
                        "physical": 0,
                        "read_ahead": 0,
                        "scans": 0,
                    },
                    "#inline_data_1": {
                        "lob_logical": 0,
                        "lob_physical": 0,
                        "lob_read_ahead": 0,
                        "logical": 7,
                        "physical": 0,
                        "read_ahead": 0,
                        "scans": 1,
                    },
                    "#tmp_1": {
                        "lob_logical": 0,
                        "lob_physical": 0,
                        "lob_read_ahead": 0,
                        "logical": 4,
                        "physical": 0,
                        "read_ahead": 0,
                        "scans": 3,
                    },
                },
            },
        ),
        (
            [
                b"This message will not be parseable and should be ignored",
                (
                    b"SQL Server parse and compile time: \n"
                    b"   CPU time = 10 ms, elapsed time = 5 ms."
                ),
                (
                    b"\n SQL Server Execution Times:\n"
                    b"   CPU time = 100 ms,  elapsed time = 0 ms."
                ),
            ],
            {
                "timings": {
                    "exec_cpu_ms": 100,
                    "exec_elapsed_ms": 0,
                    "exec_cpu_ratio": 0.0,
                    "parse_cpu_ms": 10,
                    "parse_elapsed_ms": 5,
                },
            },
        ),
    ],
)
def test_parse_statistics_messages(messages, results):
    # messages =

    timings, table_io = parse_statistics_messages(messages)

    assert timings == results["timings"]
    if "table_io" in results:
        assert table_io == results["table_io"]
