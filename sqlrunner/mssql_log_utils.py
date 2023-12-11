import re
import time
from collections import defaultdict


# from contextlib import contextmanager


class logging_cursor:
    def __init__(self, connection, sql_query, log):
        self._cursor = connection.cursor()
        self._log = log
        self._query = sql_query

    def __enter__(self):
        if self._log:
            self._messages = []
            self._cursor.connection._conn.set_msghandler(
                lambda *args: self._messages.append(args[-1])
            )
            self._cursor.execute("SET STATISTICS TIME ON")
            self._cursor.execute("SET STATISTICS IO ON")
            self._log.info("sql_query", sql_query=self._query)
            self._start = time.monotonic()
        return self._cursor

    def __exit__(self, type, value, traceback):  # noqa
        if self._log:
            duration = time.monotonic() - self._start
            timings, table_io = parse_statistics_messages(self._messages)
            self._log.info("timing_stats", duration_ms=int(duration), **timings)
            self._log.info("table_io_stats", table_io=table_io)


# @contextmanager
# def logging_cursor(connection, sql_query, log):
#     cursor = connection.cursor()
#     if log:
#         log.info("sql_query", sql_query=sql_query)
#         messages = []
#         connection._conn.set_msghandler(lambda *args: messages.append(args[-1]))
#         cursor.execute("SET STATISTICS TIME ON")
#         cursor.execute("SET STATISTICS IO ON")
#         start = time.monotonic()
#         yield cursor
#         duration = time.monotonic() - start
#         timings, table_io = parse_statistics_messages(messages)
#         log.info("timing_stats", duration_ms=int(duration), **timings)
#         log.info("table_io_stats", table_io=table_io)
#     else:
#         yield cursor


def execute_with_log(cursor, sql_query, log):
    """
    Execute `query` with `connection` while logging SQL, timing and IO information.
    """
    connection = cursor.connection
    log.info("sql_query", sql_query=sql_query)

    # https://pymssql.readthedocs.io/en/stable/ref/_mssql.html#_mssql.MSSQLConnection.set_msghandler
    messages = []
    connection._conn.set_msghandler(lambda *args: messages.append(args[-1]))
    cursor.execute("SET STATISTICS TIME ON")
    cursor.execute("SET STATISTICS IO ON")

    start = time.monotonic()
    cursor.execute(sql_query)
    duration = time.monotonic() - start

    timings, table_io = parse_statistics_messages(messages)
    log.info("timing_stats", duration_ms=int(duration), **timings)
    log.info("table_io_stats", table_io=table_io)


SQLSERVER_STATISTICS_REGEX = re.compile(
    rb"""
    .* (

    # Regex to match timing statistics messages

    SQL\sServer\s
      (?P<timing_type>parse\sand\scompile\stime|Execution\sTime)
    .* CPU\stime\s=\s(?P<cpu_ms>\d+)\sms
    .* elapsed\stime\s=\s(?P<elapsed_ms>\d+)\sms

    |

    # Regex to match IO statistics messages

    Table\s'(?P<table>[^']+)'. \s+
    Scan\scount\s (?P<scans>\d+), \s+
    logical\sreads\s (?P<logical>\d+), \s+
    physical\sreads\s (?P<physical>\d+), \s+
    read-ahead\sreads\s (?P<read_ahead>\d+), \s+
    lob\slogical\sreads\s (?P<lob_logical>\d+), \s+
    lob\sphysical\sreads\s (?P<lob_physical>\d+), \s+
    lob\sread-ahead\sreads\s (?P<lob_read_ahead>\d+)

    ) .*
    """,
    flags=re.DOTALL | re.VERBOSE,
)


def parse_statistics_messages(messages):
    """
    Accepts a list of MSSQL statistics messages and returns a dict of cumulative timing
    stats and a dict of cumulative table IO stats.
    """
    timings = {
        "exec_cpu_ms": 0,
        "exec_elapsed_ms": 0,
        "exec_cpu_ratio": 0.0,
        "parse_cpu_ms": 0,
        "parse_elapsed_ms": 0,
    }
    table_io = defaultdict(
        lambda: {
            "scans": 0,
            "logical": 0,
            "physical": 0,
            "read_ahead": 0,
            "lob_logical": 0,
            "lob_physical": 0,
            "lob_read_ahead": 0,
        }
    )
    timing_types = {b"parse and compile time": "parse", b"Execution Time": "exec"}
    for message in messages:
        if match := SQLSERVER_STATISTICS_REGEX.match(message):
            if timing_type := match["timing_type"]:
                prefix = timing_types[timing_type]
                timings[f"{prefix}_cpu_ms"] += int(match["cpu_ms"])
                timings[f"{prefix}_elapsed_ms"] += int(match["elapsed_ms"])
            elif table := match["table"]:
                table = table.decode(errors="ignore")
                # Temporary table names are, internally to MSSQL, made globally unique
                # by padding with underscores and appending a unique suffix. We need to
                # restore the original name so our stats make sense. If you've got an
                # actual temp table name with 5 underscores in it you deserve everything
                # you get.
                if table.startswith("#"):
                    table = table.partition("_____")[0]
                stats = table_io[table]
                for key in stats.keys():
                    stats[key] += int(match[key])
            else:
                # Given the structure of the regex it shouldn't be possible to get here,
                # but if somehow we did I'd rather drop the stats message than blow up
                pass  # pragma: no cover
    if timings["exec_elapsed_ms"] != 0:
        timings["exec_cpu_ratio"] = round(
            timings["exec_cpu_ms"] / timings["exec_elapsed_ms"], 2
        )
    return timings, table_io
